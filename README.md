# crawl_vip_paid_manhua
突发奇想，想通过爬虫破解付费漫画章节下载
***********************************************

** 更新：
付费章节毫无头绪，url参数找不到构造方法（加密参数无法看出规律，也不知道是不是md5还是腾讯自家的加密方式。。。。），selenium就不用说了。。。。看了一天头昏脑涨。。先缓缓吧。。

------------------------------------------------------------------------------------------------------------------------------------------

## 更新：
花了大半天，想明白两件事：<br>
1 不要挑战大厂，尤其是BAT带头的互联网企业，人家的前端工程师不是吃素的。。。<br>
2 不用非钻牛角尖，换个漫画网站爬也一样。。。。。。。

------------------------------------------------------------------------------------------------------------------------------------------

  换了网站之后，又发现这个网站也不是ajax来渲染内容的，但为啥response回来的和看到的源码就是不一样。。。。<br>
  然后只能用selenium，然后又作死想用多进程爬得快一点。。。<br>
  然后就状况百出：
        * ip代理池爬取的是免费的ip，果然不稳定得一批。。基本上爬个半分钟出一次错
        * retry模块用的不熟练，调试发现写的越多逻辑越迷
 
 *****************************************************
 反正最后爬下来了，妖怪名单！！！（曾经很喜欢的一部漫画，后来因为收费就放弃了，然鹅我卷土重来了~万能的互联网）
 ![pic1]()
        
 
 


