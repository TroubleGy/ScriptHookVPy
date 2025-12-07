#include <windows.h>
#include <Python.h>
#include <pybind11/pybind11.h>
#include <pybind11/embed.h>
#include <filesystem>
#include <vector>
#include <fstream>
#include "../inc/ScriptHookV.h"
#include "../inc/natives.h"

namespace py = pybind11;
namespace fs = std::filesystem;

std::vector<py::module_> loadedScripts;
std::ofstream logFile;

void Log(const std::string& msg)
{
    logFile << msg << std::endl;
    logFile.flush();
}

void LoadPythonScripts()
{
    fs::path scriptsPath = fs::current_path() / "pythons";

    if (!fs::exists(scriptsPath))
    {
        fs::create_directory(scriptsPath);
        return;
    }

    for (const auto& entry : fs::directory_iterator(scriptsPath))
    {
        if (entry.path().extension() == ".py")
        {
            std::string fileName = entry.path().filename().string();
            std::string moduleName = entry.path().stem().string();

            try
            {
                py::module_ script = py::module_::import(moduleName.c_str());
                loadedScripts.push_back(script);
                Log(fileName + " initialized");
            }
            catch (const py::error_already_set& e)
            {
                Log(fileName + " error: " + std::string(e.what()));
            }
        }
    }
}

void RunScripts()
{
    for (auto& script : loadedScripts)
    {
        try
        {
            if (py::hasattr(script, "update"))
            {
                script.attr("update")();
            }
        }
        catch (const py::error_already_set& e)
        {
            Log("Runtime error: " + std::string(e.what()));
        }
    }
}

void ScriptMain()
{
    logFile.open("ScriptHookVPy.log");
    Log("ScriptHookVPy initialized");

    py::scoped_interpreter python;

    py::module_ sys = py::module_::import("sys");
    sys.attr("path").attr("insert")(0, "./pythons");

    LoadPythonScripts();

    while (true)
    {
        RunScripts();
        WAIT(0);
    }
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved)
{
    if (reason == DLL_PROCESS_ATTACH)
    {
        scriptRegister(hModule, ScriptMain);
    }
    else if (reason == DLL_PROCESS_DETACH)
    {
        scriptUnregister(hModule);
        if (logFile.is_open()) logFile.close();
    }
    return TRUE;
}