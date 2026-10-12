# CMake

## Note

- 指令与大小写无关
- 参数和变量相关

## 命令

- **cmake_minimum_required()**

- **add_compile_options()**
  - 添加编译参数
  - 例如：
    ```cmake
    add_compile_options(-Wall -std=c++11 -O2)
    ```

- **project()**

- **set()**

- **add_executable()**

- **include_directories()**
  - 添加多个头文件搜索路径
  - 类比：
    ```bash
    g++ -I
    ```

- **link_directories()**
  - 添加多个库文件搜索路径
  - 类比：
    ```bash
    g++ -L
    ```

- **add_library()**
  - 例如：
    ```cmake
    add_library(tools STATIC a.cpp b.cpp c.cpp)
    ```
  - `STATIC`：静态库
  - `SHARED`：动态库
  - `OBJECT`：仅编译成目标文件，不打包成库

- **target_link_libraries()**

- **add_subdirectory()**


## CMake 内置常用变量

### 路径变量

- `CMAKE_SOURCE_DIR`：项目根源码目录
- `CMAKE_CURRENT_SOURCE_DIR`：当前 CMakeLists.txt 所在源码目录
- `CMAKE_BINARY_DIR`：项目构建输出根目录
- `CMAKE_CURRENT_BINARY_DIR`：当前目录对应的构建输出目录
- `PROJECT_SOURCE_DIR`：`project()` 命令所在源码目录
- `PROJECT_BINARY_DIR`：`project()` 对应构建目录

### 编译与编译器变量

- `CMAKE_C_COMPILER`：C 编译器路径
- `CMAKE_CXX_COMPILER`：C++ 编译器路径
- `CMAKE_C_FLAGS`：C 全局编译选项
- `CMAKE_CXX_FLAGS`：C++ 全局编译选项
- `CMAKE_BUILD_TYPE`：编译类型 Debug/Release
- `CMAKE_CXX_STANDARD`：C++ 标准版本 11/14/17/20

### 输出目录变量

- `CMAKE_RUNTIME_OUTPUT_DIRECTORY`：可执行文件输出路径
- `CMAKE_LIBRARY_OUTPUT_DIRECTORY`：动态库输出路径
- `CMAKE_ARCHIVE_OUTPUT_DIRECTORY`：静态库输出路径

### 开关、系统、安装变量

- `BUILD_SHARED_LIBS`：ON 默认生成动态库，OFF 默认生成静态库
- `CMAKE_SYSTEM_NAME`：操作系统名 Linux/Windows/Darwin
- `CMAKE_INSTALL_PREFIX`：安装根目录，Linux 默认 `/usr/local`


## 构建

### 外部构建

- 创建构建目录
  ```bash
  mkdir build
    cd build
    cmake ..
    make
  ```

### 内部构建

- 不建议
