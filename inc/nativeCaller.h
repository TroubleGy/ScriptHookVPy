#pragma once
#include <type_traits>
#include "ScriptHookV.h"
#include "types.h"

template <typename T>
static inline void nativePush(T val)
{
    nativePush64((UINT64)val);
}

template <>
static inline void nativePush<float>(float val)
{
    nativePush64(*(UINT64*)&val);
}

template <typename T>
static inline T invoke(UINT64 hash)
{
    nativeInit(hash);

    if constexpr (std::is_same_v<T, void> || std::is_same_v<T, Void>)
    {
        nativeCall();
    }
    else if constexpr (std::is_same_v<T, const char*>)
    {
        return (const char*)nativeCall();
    }
    else if constexpr (std::is_same_v<T, Vector3>)
    {
        UINT64* result = nativeCall();
        Vector3 vec;
        vec.x = *(float*)&result[0];
        vec.y = *(float*)&result[1];
        vec.z = *(float*)&result[2];
        return vec;
    }
    else
    {
        return *(T*)nativeCall();
    }
}

template <typename R, typename... Args>
static inline R invoke(UINT64 hash, Args... args)
{
    nativeInit(hash);
    (nativePush(args), ...);

    if constexpr (std::is_same_v<R, void> || std::is_same_v<R, Void>)
    {
        nativeCall();
    }
    else if constexpr (std::is_same_v<R, const char*>)
    {
        return (const char*)nativeCall();
    }
    else if constexpr (std::is_same_v<R, Vector3>)
    {
        UINT64* result = nativeCall();
        Vector3 vec;
        vec.x = *(float*)&result[0];
        vec.y = *(float*)&result[1];
        vec.z = *(float*)&result[2];
        return vec;
    }
    else
    {
        return *(R*)nativeCall();
    }
}