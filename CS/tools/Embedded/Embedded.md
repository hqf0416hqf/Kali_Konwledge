嵌入式不是“学某一种芯片”，而是学习“让计算机进入真实设备，并直接控制硬件”。

芯片之所以这么多，是因为不同设备对性能、功耗、实时性、成本、外设、体积的要求完全不同。

可以把嵌入式知识体系画成这样：

# 嵌入式系统知识体系

```text
嵌入式系统
│
├── 硬件
│   ├── CPU
│   ├── RAM
│   ├── Flash
│   ├── 外部存储
│   └── 外设
│       ├── GPIO
│       ├── UART
│       ├── SPI
│       ├── I2C
│       ├── CAN
│       ├── ADC
│       ├── Timer
│       └── PWM
│
├── CPU架构 / ISA
│   ├── Arm
│   ├── x86 / x86-64
│   └── RISC-V
│
├── 芯片
│   ├── MCU
│   │   ├── 51
│   │   ├── STM32
│   │   ├── ESP32
│   │   ├── GD32
│   │   ├── RP2040
│   │   ├── MSP430
│   │   └── NXP MCU
│   │
│   └── MPU / SoC
│       ├── RK
│       └── Raspberry Pi
│
├── Firmware / Driver
│   ├── Bootloader
│   ├── BSP
│   ├── HAL
│   └── Driver
│
├── 操作系统
│   ├── 裸机
│   ├── RTOS
│   │   ├── FreeRTOS
│   │   ├── Zephyr
│   │   └── RT-Thread
│   └── 通用 OS
│       ├── Linux
│       ├── Android
│       └── ...
│
└── 应用软件
    ├── C / C++
    ├── Python
    ├── Assembly
    ├── OpenCV
    ├── ROS2
    └── AI
```

嵌入式系统
- 硬件 
    - CPU
    - RAM
    - 硬盘
        - HDD
        - SDD
    - 外设
    - GPU
- 芯片
    - MCU
        STM32 
        STM51   
        STM32
        ESP32
        NXP
        GD32
        RP2040
        MSP430
    - MCP
    - Soc
- 驱动 / 硬件抽象
- CPU指令集架构
    - 一个操作系统可以支持多种架构
    - ARM
    - X86
    - X86_64
    - ...
- 系统
    - 裸机
    - RTOS 
        - FreeRTOS
        - Zephyr
        - RT-Thread
    - 大型OS
        - Linux
        - MACOS
        - Windows
        - Android
- 软件（使用的技术栈）
    - C/C++ 
    - 汇编
    - OS


    

