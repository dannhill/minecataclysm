// Native Windows process supervisor. CDDA remains gameplay/save authority.
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <winsock2.h>
#include <windows.h>
#include <shlobj.h>
#include <shellapi.h>
#include <objbase.h>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <stdexcept>
#include <chrono>
#include "cwm/product_language.hpp"
namespace fs = std::filesystem;
static bool cancelled = false;
static HWND status_label = nullptr;
static std::string utf8(const std::wstring &s) {
    if (s.empty()) return {};
    const int n=WideCharToMultiByte(CP_UTF8,0,s.data(),int(s.size()),nullptr,0,nullptr,nullptr);
    std::string out(n,'\0');WideCharToMultiByte(CP_UTF8,0,s.data(),int(s.size()),out.data(),n,nullptr,nullptr);return out;
}
static std::wstring wide(const std::string &s) {
    if (s.empty()) return {};
    const int n=MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,s.data(),int(s.size()),nullptr,0);
    std::wstring out(n,L'\0');MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,s.data(),int(s.size()),out.data(),n);return out;
}
static std::wstring quoted(const std::wstring &arg) {
    std::wstring out=L"\"";unsigned backslashes=0;
    for (wchar_t c:arg) {
        if(c==L'\\')++backslashes;
        else {out.append(backslashes*(c==L'"'?2:1),L'\\');backslashes=0;if(c==L'"')out+=L'\\';out+=c;}
    }
    out.append(backslashes*2,L'\\');return out+L'"';
}
static LRESULT CALLBACK window_proc(HWND w,UINT msg,WPARAM a,LPARAM b) {
    if(msg==WM_CLOSE){cancelled=true;return 0;}
    return DefWindowProcW(w,msg,a,b);
}
static void pump() { MSG msg;while(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){TranslateMessage(&msg);DispatchMessageW(&msg);} }
static void status(HWND window,const wchar_t *text) {SetWindowTextW(status_label,text);ShowWindow(window,SW_SHOWNORMAL);UpdateWindow(window);pump();}
static std::string setting(const fs::path &file,const std::string &key) {
    std::ifstream input(file);std::string line,value;
    while(std::getline(input,line)){
        const auto hash=line.find('#');if(hash!=std::string::npos)line.erase(hash);
        const auto eq=line.find('=');if(eq==std::string::npos)continue;
        auto trim=[](std::string x){const auto first=x.find_first_not_of(" \t\r");return first==std::string::npos?std::string():x.substr(first,x.find_last_not_of(" \t\r")-first+1);};
        if(trim(line.substr(0,eq))==key)value=trim(line.substr(eq+1));
    }return value;
}
static void save_preference(const fs::path &path,const std::string &code) {
    const auto temp=path.wstring()+L".new";
    {std::ofstream out{fs::path(temp)};out<<"# Product presentation preference\ncwm_language = "<<code<<'\n';out.flush();if(!out)throw std::runtime_error("Cannot save the language preference.");}
    if(!MoveFileExW(temp.c_str(),path.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))throw std::runtime_error("Cannot replace the language preference.");
}
struct Handle {
    HANDLE value{nullptr};Handle()=default;explicit Handle(HANDLE h):value(h){}
    ~Handle(){if(value && value!=INVALID_HANDLE_VALUE)CloseHandle(value);}
    Handle(const Handle&)=delete;Handle&operator=(const Handle&)=delete;
};
struct Process {Handle process;DWORD thread_id{0};};
static void spawn(Process &child,const fs::path &exe,const std::vector<std::wstring> &args,const fs::path &cwd,const fs::path &log,HANDLE job) {
    SECURITY_ATTRIBUTES sa{sizeof(sa),nullptr,TRUE};
    Handle output(CreateFileW(log.c_str(),GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,&sa,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr));
    Handle input(CreateFileW(L"NUL",GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,&sa,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr));
    if(output.value==INVALID_HANDLE_VALUE||input.value==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot create game log files.");
    std::wstring command=quoted(exe.wstring());for(const auto &arg:args)command+=L" "+quoted(arg);
    STARTUPINFOW si{};si.cb=sizeof(si);si.dwFlags=STARTF_USESTDHANDLES;si.hStdInput=input.value;si.hStdOutput=si.hStdError=output.value;
    PROCESS_INFORMATION pi{};
    if(!CreateProcessW(exe.c_str(),command.data(),nullptr,nullptr,TRUE,CREATE_NO_WINDOW|CREATE_SUSPENDED,nullptr,cwd.c_str(),&si,&pi))
        throw std::runtime_error("Cannot start a bundled game component (Windows error "+std::to_string(GetLastError())+").");
    child.process.value=pi.hProcess;child.thread_id=pi.dwThreadId;Handle thread(pi.hThread);
    if(!AssignProcessToJobObject(job,pi.hProcess)){TerminateProcess(pi.hProcess,1);throw std::runtime_error("Cannot supervise the game processes.");}
    ResumeThread(pi.hThread);
}
static DWORD exit_code(HANDLE process) {DWORD code=0;GetExitCodeProcess(process,&code);return code;}
static bool alive(HANDLE process) {return process && WaitForSingleObject(process,0)==WAIT_TIMEOUT;}
static unsigned local_port() {
    WSADATA data{};if(WSAStartup(MAKEWORD(2,2),&data))throw std::runtime_error("Cannot initialize local networking.");
    SOCKET s=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP);sockaddr_in addr{};addr.sin_family=AF_INET;addr.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
    int size=sizeof(addr);bool ok=s!=INVALID_SOCKET && bind(s,reinterpret_cast<sockaddr*>(&addr),size)==0 && getsockname(s,reinterpret_cast<sockaddr*>(&addr),&size)==0;
    if(s!=INVALID_SOCKET)closesocket(s);WSACleanup();if(!ok)throw std::runtime_error("Cannot allocate a local game port.");return ntohs(addr.sin_port);
}
int WINAPI wWinMain(HINSTANCE instance,HINSTANCE,LPWSTR,int) {
    fs::path logs;Process server,client;Handle stop,ready,job,lock;HWND window=nullptr;std::string initial="en";
    fs::path preferences,config;
    try {
        std::vector<wchar_t> module(32768);DWORD len=GetModuleFileNameW(nullptr,module.data(),DWORD(module.size()));
        if(!len || len>=module.size())throw std::runtime_error("Cannot find the game folder.");
        const fs::path root=fs::path(std::wstring(module.data(),len)).parent_path();
        PWSTR local=nullptr;if(FAILED(SHGetKnownFolderPath(FOLDERID_LocalAppData,KF_FLAG_CREATE,nullptr,&local)))throw std::runtime_error("Cannot find your Windows save folder.");
        fs::path user=fs::path(local)/L"Minecataclysm";CoTaskMemFree(local);
        int argc=0;LPWSTR *argv=CommandLineToArgvW(GetCommandLineW(),&argc);
        for(int i=1;i<argc;++i)if(std::wstring(argv[i])==L"--userdir" && i+1<argc)user=argv[++i];else {LocalFree(argv);throw std::runtime_error("Unknown launcher option.");}
        LocalFree(argv);fs::create_directories(user);
        const std::wstring mutex=L"Local\\Minecataclysm-"+std::to_wstring(std::hash<std::wstring>{}(fs::absolute(user).wstring()));
        lock.value=CreateMutexW(nullptr,TRUE,mutex.c_str());
        if(!lock.value || GetLastError()==ERROR_ALREADY_EXISTS){MessageBoxW(nullptr,L"Minecataclysm is already running.",L"Minecataclysm",MB_OK|MB_ICONINFORMATION);return 0;}
        GUID guid; if(FAILED(CoCreateGuid(&guid)))throw std::runtime_error("Cannot create a private game session.");wchar_t id[64];StringFromGUID2(guid,id,64);
        const std::wstring unique=id;logs=user/L"logs"/unique;fs::create_directories(logs);
        preferences=user/L"presentation-language.conf";initial=setting(preferences,"cwm_language");if(!cwm::product_language(initial))initial="en";
        const auto *language=cwm::product_language(initial);
        const fs::path runtime=root/L"runtime",bin=runtime/L"bin",world=user/L"presentation",native=user/L"cdda";
        for(const auto &p:{bin/L"cdda-server.exe",bin/L"luanti.exe",runtime/L"cdda/data/core",runtime/L"games/cdda_voxel/game.conf"})
            if(!fs::exists(p))throw std::runtime_error("The game package is incomplete. Reinstall Minecataclysm.");
        fs::create_directories(world);fs::create_directories(native);fs::create_directories(user/L"client");
        if(!fs::exists(world/L"world.mt")){std::ofstream out(world/L"world.mt");out<<"gameid = cdda_voxel\nbackend = sqlite3\nplayer_backend = sqlite3\nauth_backend = sqlite3\nload_mod_cdda_nodes = true\nload_mod_cdda_entities = true\n";if(!out)throw std::runtime_error("Cannot create the presentation world.");}
        config=user/L"client.conf";
        std::ostringstream settings;
        if(fs::exists(config)){std::ifstream old(config);settings<<old.rdbuf();}
        {std::ifstream defaults(runtime/L"defaults.conf");if(!defaults)throw std::runtime_error("The default game configuration is missing.");settings<<'\n'<<defaults.rdbuf();}
        const std::wstring endpoint=L"\\\\.\\pipe\\Minecataclysm-"+unique;
        settings<<"\nkeymap_quicktune_next = KEY_F7\nkeymap_quicktune_prev = KEY_F8\nbind_address = 127.0.0.1\nport = "<<local_port()<<"\ncwm_socket_path = "<<utf8(endpoint)
                <<"\ncwm_language = "<<initial<<"\nlanguage = "<<language->engine_locale<<"\n";
        {std::ofstream out(config);out<<settings.str();if(!out)throw std::runtime_error("Cannot write your game settings.");}
        SetEnvironmentVariableW(L"CDDA_LOCALE_DIR",(runtime/L"cdda/lang/mo").c_str());
        SetEnvironmentVariableW(L"MINETEST_USER_PATH",(user/L"client").c_str());
        const std::wstring stop_name=L"Local\\Minecataclysm-Stop-"+unique,ready_name=L"Local\\Minecataclysm-Ready-"+unique;
        stop.value=CreateEventW(nullptr,TRUE,FALSE,stop_name.c_str());ready.value=CreateEventW(nullptr,TRUE,FALSE,ready_name.c_str());
        job.value=CreateJobObjectW(nullptr,nullptr);JOBOBJECT_EXTENDED_LIMIT_INFORMATION limit{};limit.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        if(!stop.value||!ready.value||!job.value||!SetInformationJobObject(job.value,JobObjectExtendedLimitInformation,&limit,sizeof(limit)))throw std::runtime_error("Cannot initialize the game supervisor.");
        WNDCLASSW wc{};wc.lpfnWndProc=window_proc;wc.hInstance=instance;wc.lpszClassName=L"MinecataclysmLauncher";wc.hbrBackground=reinterpret_cast<HBRUSH>(COLOR_WINDOW+1);wc.hCursor=LoadCursor(nullptr,IDC_ARROW);wc.hIcon=LoadIcon(nullptr,IDI_APPLICATION);RegisterClassW(&wc);
        window=CreateWindowW(wc.lpszClassName,L"Minecataclysm",WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU,CW_USEDEFAULT,CW_USEDEFAULT,460,145,nullptr,nullptr,instance,nullptr);
        status_label=CreateWindowW(L"STATIC",L"",WS_CHILD|WS_VISIBLE|SS_CENTER,15,35,420,55,window,nullptr,instance,nullptr);
        SendMessageW(status_label,WM_SETFONT,reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)),TRUE);
        status(window,L"Preparing your world...\nThe first start can take a few minutes.");
        spawn(server,bin/L"cdda-server.exe",{L"--socket",endpoint,L"--world",L"cdda_voxel",L"--continuous",L"--language",wide(initial),L"--userdir",native.wstring(),L"--datadir",(runtime/L"cdda/data").wstring(),L"--stop-event",stop_name,L"--ready-event",ready_name},runtime,logs/L"cdda.log",job.value);
        const auto began=GetTickCount64();
        while(WaitForSingleObject(ready.value,0)!=WAIT_OBJECT_0){
            pump();if(cancelled)throw std::runtime_error("Game startup cancelled.");
            if(!alive(server.process.value))throw std::runtime_error("The simulation could not start. See the game logs.");
            if(GetTickCount64()-began>300000)throw std::runtime_error("World preparation is taking too long. See the game logs.");Sleep(30);
        }
        status(window,L"Opening Minecataclysm...");
        spawn(client,bin/L"luanti.exe",{L"--go",L"--world",world.wstring(),L"--gameid",L"cdda_voxel",L"--config",config.wstring(),L"--logfile",(logs/L"engine.log").wstring()},runtime,logs/L"client.log",job.value);
        ShowWindow(window,SW_HIDE);
        while(alive(client.process.value)){
            pump();if(cancelled){TerminateProcess(client.process.value,1);break;}
            if(!alive(server.process.value)){
                // Death is a native successful shutdown. A native failure must
                // be surfaced instead of silently leaving a frozen client.
                if(exit_code(server.process.value)==0){PostThreadMessageW(client.thread_id,WM_QUIT,0,0);Sleep(250);if(alive(client.process.value))TerminateProcess(client.process.value,0);break;}
                throw std::runtime_error("The simulation stopped unexpectedly. See the game logs.");
            }Sleep(50);
        }
        status(window,L"Saving your game...\nPlease wait before closing Windows.");
        SetEvent(stop.value);
        while(alive(server.process.value)){pump();Sleep(30);}
        const auto chosen=setting(config,"cwm_language");if(cwm::product_language(chosen)&&chosen!=initial)save_preference(preferences,chosen);
        if(exit_code(server.process.value)!=0)throw std::runtime_error("The simulation reported a save error. Your existing saves have been retained; see the game logs.");
        if(client.process.value && exit_code(client.process.value)!=0 && !cancelled)throw std::runtime_error("The 3D client stopped unexpectedly. See the game logs.");
        DestroyWindow(window);return 0;
    } catch(const std::exception &error) {
        if(stop.value)SetEvent(stop.value);
        // Stop presentation first and give the native owner a chance to save.
        if(alive(client.process.value))TerminateProcess(client.process.value,1);
        if(alive(server.process.value)){
            if(window)status(window,L"Saving before closing...");
            const auto began=GetTickCount64();while(alive(server.process.value)&&GetTickCount64()-began<60000){pump();Sleep(30);}
        }
        std::wstring message=wide(error.what());if(!logs.empty())message+=L"\n\nLogs: "+logs.wstring();
        MessageBoxW(window,message.c_str(),L"Minecataclysm",MB_OK|MB_ICONERROR);
        if(window)DestroyWindow(window);return 1;
    }
}
