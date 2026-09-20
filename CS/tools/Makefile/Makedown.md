# Markdown

## 标题

```markdown
# 一级标题
## 二级标题
### 三级标题
```
`#` 越多，标题级别越低。

## 文字

```markdown
**粗体**
*斜体*
~~删除线~~
`行内代码`
```

效果：

**粗体**     
*斜体*      
~~删除线~~   
`行内代码`

## 列表

### 无序列表
```markdown
- 内容
- 内容
  - 子内容
```

### 有序列表
```markdown
1. 内容
2. 内容
3. 内容
```

### 任务列表
```markdown
- [ ] 未完成
- [x] 已完成
```


## 代码块

基本格式：

````markdown
```语言
代码
```
````

例如：

````markdown
```cpp
#include <iostream>

int main()
{
    return 0;
}
```
````

常见语言：

```text
cpp
bash
python
cmake
makefile
text
```

## 引用

```markdown
> 这是一段引用
```

效果：
> 这是一段引用

## 链接

```markdown
[显示的文字](https://example.com)
```

例如：
```markdown
[GitHub](https://github.com)
```

## 图片

```markdown
![图片描述](图片路径)
```

例如：

```markdown
![logo](./image/logo.png)
```

## 分割线

```markdown
---
```

效果：

---

## 表格

```markdown
| 名称 | 类型 | 说明 |
|---|---|---|
| name | string | 名字 |
| age | int | 年龄 |
```

效果：

| 名称   | 类型     | 说明 |
| ---- | ------ | -- |
| name | string | 名字 |
| age  | int    | 年龄 |

## 换行与段落

空一行表示新的段落：

```markdown
第一段。

第二段。
```

行末加两个空格可以换行：

```markdown
第一行  
第二行
```

## 转义字符

Markdown 中某些符号有特殊含义。

在符号前加 `\` 可以取消其 Markdown 含义：

```markdown
\# 不是标题
\* 不是斜体
\` 不是代码
```
效果（可以输出具体的字符，不被翻译makedown）
\#  \*  \_  \`  \[  \]


