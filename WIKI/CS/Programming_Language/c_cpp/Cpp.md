# CPP

## this
作用1：区分成员变量/形参
例如 
```CPP
    class Person{
    public:
        int age;  
        Person(int age) : thid->age=age{}
    };

    //提供另一种赋值方法（初始化列表），不用this 
    class Person{
    public:
        int age;
        // 构造函数才支持初始化列表
        Person(int age) : age(age){}
    };=
```

 
## 


