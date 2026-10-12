# //草稿//

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


RAM
Flash
EEPROM

外设
GPU
MPU
ISP

看门狗

烧录 

CPU
MCU
MPU


电机上电，MCU可能重启

Encoder：编码器，测电机/车轮运动

IMU：测运动状态的传感器
最基础的 6 轴 IMU：
3轴加速度计
+
3轴陀螺仪'
进一步通过算法估计：姿态
比如：
    车正在旋转
    车有没有倾斜
    车转了多少
通常：
    IMU
    ↓
    SPI / I2C
    ↓
    STM32

                 MCU
                  │
          ┌───────┴───────┐
          │               │
       CPU核心          外设控制器
                          │
             ┌────────────┼────────────┐
             ↓            ↓            ↓
           UART          SPI          I²C
             │            │            │
             ↓            ↓            ↓
          TX/RX      MOSI/MISO...    SDA/SCL
             └────────────┼────────────┘
                          ↓
                       GPIO复用
                          ↓
                       物理引脚



| 模块         | 是什么                   |
| ---------- | --------------------- |
| **DMA**    | 让外设和内存直接搬数据，减少 CPU 参与 |
| **DVP**    | 摄像头并行数据接口             |
| **JTAG**   | 调试/下载/测试接口            |
| **AES**    | 加密算法硬件加速              |
| **OTP**    | 一次性可编程存储区域            |
| **FPIOA**  | 芯片引脚功能映射系统            |
| **SRAM**   | 内存                         |
| **FFT**    | 快速傅里叶变换硬件加速          |
| **GPIO**   | 通用数字输入输出              |
| **RTC**    | 实时时钟                    |
| **Timer**  | 定时器                      |
| **PWM**    | 脉宽调制                     |
| **WDT** （WatchDog Timer） | 看门狗定时器  |
| **SHA256** | 哈希算法硬件加速              |


STM32F103 能通过定时器产生 PWM，K210 的 CanMV 也提供 PWM 相关接口。www.st.com
PWM 是一种信号：周期性地输出高、低电平。
例如每个周期中：
- 30% 的时间输出高电平，叫 30% 占空比；
- 70% 的时间输出高电平，叫 70% 占空比。
但是，主控引脚主要用于传递控制信号，不能承担电机启动时的大电流。