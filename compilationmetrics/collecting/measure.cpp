extern "C" {
#include <fcntl.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
} // extern "C"

#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <ostream>
#include <sstream>
#include <string>

void usage(std::ostream& out, const char* argv0) {
    const char indent[] = "    ";
    out << "measure - run a command and write its resource consumption as JSON to a file\n\n"
        << "usage:\n\n"
        << indent << argv0 << " <URI> <COMMAND> ...\n"
        << indent << indent << "Run COMMAND and write its resource consumption as JSON to URI,\n"
        << indent << indent << "where URI is either of the form \"file:///path/to/file\" or \n"
        << indent << indent << "\"fd://integer_file_descriptor\".  The path to the COMMAND must \n"
        << indent << indent << "be fully qualified.\n\n"
        << indent << argv0 << " --help\n"
        << indent << argv0 << " -h\n"
        << indent << indent << "Print this message.\n\n";
}

bool is_help_flag(const char* arg) {
    return std::strcmp(arg, "-h") == 0 || std::strcmp(arg, "--help") == 0;
}

std::ostream& operator<<(std::ostream& stream, const ::timeval& value) {
    return stream << "{\"" << "tv_sec\": " << value.tv_sec
        << ", \"tv_usec\": " << value.tv_usec << "}";
}

int wait_and_measure_child(int pid, int reporting_fd) {
    int status;
    for (;;) {
        if (::waitpid(pid, &status, 0) != pid) {
            const int error = errno;
            switch (error) {
                case EINTR: continue;
                default:
                    std::cerr << "waitpid(...) failed: " << std::strerror(error) << "\n";
                    return error;
            }
        } else {
            break; // Successfully waited for the child to terminate.
        }
    }

    // Get resource consumption of child process (and, I believe, all
    // descendants).
    ::rusage usage = {};
    if(::getrusage(RUSAGE_CHILDREN, &usage)) {
        return errno;
    }

    // On POSIX, we have at least:
    //
    //     struct rusage {
    //         struct timeval ru_utime;  /* User time used. */ 
    //         struct timeval ru_stime;  /* System time used. */ 
    //     };
    //
    // On Linux, we have at least:
    //
    //     struct rusage {
    //         struct timeval ru_utime; /* user CPU time used */
    //         struct timeval ru_stime; /* system CPU time used */
    //         long   ru_maxrss;        /* maximum resident set size */
    //         long   ru_ixrss;         /* integral shared memory size */
    //         long   ru_idrss;         /* integral unshared data size */
    //         long   ru_isrss;         /* integral unshared stack size */
    //         long   ru_minflt;        /* page reclaims (soft page faults) */
    //         long   ru_majflt;        /* page faults (hard page faults) */
    //         long   ru_nswap;         /* swaps */
    //         long   ru_inblock;       /* block input operations */
    //         long   ru_oublock;       /* block output operations */
    //         long   ru_msgsnd;        /* IPC messages sent */
    //         long   ru_msgrcv;        /* IPC messages received */
    //         long   ru_nsignals;      /* signals received */
    //         long   ru_nvcsw;         /* voluntary context switches */
    //         long   ru_nivcsw;        /* involuntary context switches */
    // };

    std::ostringstream json_stream;
    #define ENTRY(NAME) "    \"" #NAME "\": " << usage.NAME 
    json_stream << "{\n"
        << ENTRY(ru_utime) << ",\n"
        << ENTRY(ru_stime) << ",\n"
        << ENTRY(ru_maxrss) << ",\n"
        << ENTRY(ru_inblock) << ",\n"
        << ENTRY(ru_oublock) << ",\n"
        << ENTRY(ru_nswap) << "\n"
        << "}";
    
    const std::string json = json_stream.str();
    const char* buffer = json.c_str();
    const char* const end = json.c_str() + json.size();
    while (buffer != end) {
        const int rcode = ::write(reporting_fd, buffer, end - buffer);
        if (rcode == -1) {
            const int error = errno;
            switch (error) {
                case EINTR: continue;
                default:
                    std::cerr << "Unable to write(...) JSON to file descriptor " << reporting_fd << ": " << std::strerror(error) << "\n";
                    return error;
            }
        }
        buffer += rcode;
    }

    return 0;
}

int parse_and_open(const std::string& uri) {
    const std::string file_scheme = "file://";
    const std::string fd_scheme = "fd://";
    int fd = 0;
    
    if (uri.substr(0, file_scheme.size()) == file_scheme) {
        const std::string path = uri.substr(file_scheme.size());
        const int permissions = 0660;
        const int rcode = ::open(path.c_str(), O_WRONLY | O_CREAT, permissions);
        if (rcode == -1) {
            const int error = errno;
            std::cerr << "Unable to open file \"" << path << "\": " << std::strerror(error) << "\n";
        } else {
            fd = rcode;
        }
    } else if (uri.substr(0, fd_scheme.size()) == fd_scheme) {
       fd = std::atoi(uri.substr(fd_scheme.size()).c_str());
    } else {
        std::cerr << "Output URI has unrecognized scheme: " << uri << "\n";
    }

    return fd;
}

int main(int argc, char* argv[]) {
    if (argc == 1) {
        usage(std::cerr, argv[0]);
        return 1;
    }
    if (argc == 2 && is_help_flag(argv[1])) {
        usage(std::cout, argv[0]);
        return 0;
    }

    // Parse the file descriptor to which we'll write the child process's
    // resource consumption as JSON.
    const int reporting_fd = parse_and_open(argv[1]);
    if (reporting_fd == 0) {
        std::cerr << "Unable to parse/open a file from the specified argument: "
            << argv[1] << "\n";
        return 1;
    }

    class FdGuard {
        int fd;
      public:
        explicit FdGuard(int fd) : fd(fd) {}
        ~FdGuard() { ::close(fd); }
    } guard(reporting_fd);

    char** const command = argv + 2;

    ::pid_t parent = ::getpid();
    ::pid_t pid = ::fork();

    if (pid == -1) {
        const int error = errno;
        std::cerr << "fork() failed: " << std::strerror(error) << "\n";
        return error;
    } else if (pid > 0) {
        // We are the parent.
        return wait_and_measure_child(pid, reporting_fd);
    } else {
        // We are the child.
        ::execv(command[0], command);
        const int error = errno;
        std::cerr << "execv(...) failed: " << std::strerror(error) << "\n";
        return error;
    }
}
