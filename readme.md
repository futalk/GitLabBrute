# 原作者：https://github.com/9bie/GitLabBrute

- 原作者的脚本会在0和1反复横跳，修改脚本遍历用户后进行爆破
- 脚本内遍历到50可在脚本的`for i in range(50):`修改

# 用法

- 该脚本使用`/api/v4/users/`遍历gitlab用户名，遍历后进行爆破

```
python main.py http://target.com
```

