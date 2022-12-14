from . create_certificate import generate_certificate, check_ips
import os, re
import subprocess
from configparser import SafeConfigParser
import shutil
import logging
_logger = logging.getLogger(__name__)


"""
TODO: EDGE-CASE: 1. TO GREP PROXY PASS OUT OF MULTIPLE LOCATION BLOCK.
normal vhost copy part 
"""

CLIENT_EMAIL = "saasclient@tele-saas.tele.studio"
WEBROOT_PATH = "/usr/share/nginx/html/" 
REVERSE_PROXY_CHECK = "sudo nginx -t"
REVERSE_PROXY_RELOAD = "sudo nginx -s reload"

def execute_on_shell(cmd):
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        _logger.info(e)
        return False

def grep_backends_from_conf(tele_saas_data, subdomain):
    conf_path = os.path.join(tele_saas_data, subdomain+".conf")
    # _logger.info(conf_path)
    cmd = "grep LONGPOLLINGBACKEND" + conf_path
    grep_data = subprocess.Popen("grep LONGPOLLINGBACKEND " + conf_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = grep_data.communicate()

    if err:
        _logger.info("Couldn't get LONGPOLLINGBACKEND PORT")
    # _logger.info(out.decode().strip().split(';')[0].split(' ')[-1])
    longpolling_backend = out.decode().strip().split(';')[0].split(' ')[-1].split('//')[-1]
    grep_data = subprocess.Popen("grep TELEBACKEND " + conf_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = grep_data.communicate()
    if err:
        _logger.info("Couldn't get TELEBACKEND PORT")
    tele_backend = out.decode().strip().split(';')[0].split(' ')[-1].split('//')[-1]
    # _logger.info(longpolling_backend, tele_backend)

    return tele_backend, longpolling_backend

def replace_placeholders(vhost_file, tele_backend, longpolling_backend, custom_domain):
    cmd = "sed -i \"s/LONG_BACKEND_TO_BE_REPLACED/%s/g\" %s"%(longpolling_backend,vhost_file)
    if not execute_on_shell(cmd):
        _logger.info("Couldn't Replace Port!!")
        return False
    cmd = "sed -i \"s/BACKEND_TO_BE_REPLACED/%s/g\" %s"%(tele_backend,vhost_file)
    if not execute_on_shell(cmd):
        _logger.info("Couldn't Replace Port!!")
        return False
    cmd = "sed -i \"s/DOMAIN_TO_BE_REPLACED/%s/g\"  %s"%(custom_domain,vhost_file)
    if not execute_on_shell(cmd):
        _logger.info("Couldn't Replace Subdomain!!")
        return False
    if not execute_on_shell(REVERSE_PROXY_CHECK):
        _logger.info("Couldn't Replace Subdomain!!")
        os.remove(vhost_file)
        _logger.info("%s vhost file removed"%vhost_file)
        return False
    if not execute_on_shell(REVERSE_PROXY_RELOAD):
        _logger.info("Couldn't Replace Subdomain!!")
        os.remove(vhost_file)
        _logger.info("%s vhost file removed"%vhost_file)
        return False
    return True

def create_vhost_redirect(custom_domain, docker_vhosts):
    new_conf = os.path.join(docker_vhosts, custom_domain+".conf")
    if os.path.exists(new_conf):
        custom_domain_vhost = open(new_conf, 'a+')
        vhosttemplateredirect = open(os.path.join(docker_vhosts, "vhosttemplateredirect.txt"))
        custom_domain_vhost.write("\n\n" + vhosttemplateredirect.read())
        
        custom_domain_vhost.close()
        vhosttemplateredirect.close()
        
        cmd = "sed -i \"s/DOMAIN_TO_BE_REPLACED/%s/g\"  %s"%(custom_domain, new_conf)
        if not execute_on_shell(cmd):
            _logger.info("Couldn't Replace Subdomain!!")
            return False
        if not execute_on_shell(REVERSE_PROXY_CHECK):
            _logger.info("Couldn't Replace Subdomain!!")
            return False
        if not execute_on_shell(REVERSE_PROXY_RELOAD):
            _logger.info("Couldn't Replace Subdomain!!")
            return False
    else:
        _logger.info("File not created")
        return False

def create_vhost_https(subdomain, custom_domain, tele_backend, longpolling_backend, docker_vhosts="/opt/tele/Tele-SAAS-Data/docker_vhosts"):
    #sed -i 's/.*ssl_certificate\ .*/ ssl_certificate \/this\/is\/test/' ssl.conf
    new_conf = os.path.join(docker_vhosts, custom_domain+".conf")
    if os.path.exists(new_conf):
        os.remove(new_conf)
    shutil.copyfile(os.path.join(docker_vhosts, "vhosttemplatehttps.txt"), os.path.join(docker_vhosts, custom_domain+".conf"))
    # new_conf = custom_domain+".conf" #only for testing the code
    certificate_path = os.path.join("/etc/letsencrypt/live/", custom_domain + "/fullchain.pem")
    privkey_path = os.path.join("/etc/letsencrypt/live/", custom_domain + "/privkey.pem")
    cmd = "sed -i 's/.*ssl_certificate .*/ ssl_certificate %s;/' %s"%(certificate_path.replace("/", "\/"), new_conf)
    if not execute_on_shell(cmd):
        _logger.info("Couldn't add ssl certificate path")
        return False
    cmd = "sed -i 's/.*ssl_certificate_key .*/ ssl_certificate_key %s;/' %s"%(privkey_path.replace("/", "\/"), new_conf)
    if not execute_on_shell(cmd):
        _logger.info("Couldn't add ssl key in vhostfile")
        return False
    return replace_placeholders(new_conf, tele_backend, longpolling_backend, custom_domain)

def create_vhost_http(subdomain, custom_domain, tele_backend, longpolling_backend, docker_vhosts="/opt/tele/Tele-SAAS-Data/docker_vhosts", ssl_flag=False):
    #sed -i 's/.*ssl_certificate\ .*/ ssl_certificate \/this\/is\/test/' ssl.conf
    new_conf = os.path.join(docker_vhosts, custom_domain+".conf")
    _logger.info(locals()) 
    if False and ssl_flag:
        shutil.copyfile(os.path.join(docker_vhosts, "vhosttemplatehttps.txt"), os.path.join(docker_vhosts, custom_domain+".conf"))
        # new_conf = custom_domain+".conf" #only for testing the code
        certificate_path = os.path.join("/etc/letsencrypt/live/", custom_domain + "/fullchain.pem")
        privkey_path = os.path.join("/etc/letsencrypt/live/", custom_domain + "/privkey.pem")
        cmd = "sed -i 's/.*ssl_certificate .*/ ssl_certificate %s;/' %s"%(certificate_path.replace("/", "\/"), new_conf)
        if not execute_on_shell(cmd):
            _logger.info("Couldn't add ssl certificate path")
            return False
        cmd = "sed -i 's/.*ssl_certificate_key .*/ ssl_certificate_key %s;/' %s"%(privkey_path.replace("/", "\/"), new_conf)
        if not execute_on_shell(cmd):
            _logger.info("Couldn't add ssl key in vhostfile")
            return False
        return replace_placeholders(new_conf, tele_backend, longpolling_backend, custom_domain)        
    else:
        shutil.copyfile(os.path.join(docker_vhosts, "vhosttemplatehttp.txt"), os.path.join(docker_vhosts, custom_domain+".conf"))
        return replace_placeholders(new_conf, tele_backend, longpolling_backend, custom_domain)

def reload_nginx():
    if not execute_on_shell("sudo nginx -t"):
        _logger.info("Error in nginx config!!.Syntax test Failed")
        return False
    if not execute_on_shell("sudo nginx -s reload"):
        _logger.info("Error reloading Nginx")
        return False
    return True

def remove_vhost(domain, docker_vhosts):
    if os.path.exists(os.path.join(docker_vhosts, domain + ".conf")):
        os.remove(os.path.join(docker_vhosts, domain + ".conf"))
        _logger.info("%s removed successfully"%domain)
        reload_nginx()
    else:
        _logger.info("Vhost does not exists")

def read_path_saas_conf(module_path):
    _logger.info("Reading saas.conf")
    saas_conf_path = os.path.join(module_path, "models/lib/saas.conf")
    _logger.info(saas_conf_path)
    parser = SafeConfigParser()
    parser.read(saas_conf_path)
    tele_saas_data = parser.get("options", "tele_saas_data")

    return tele_saas_data

def run_certbot(custom_domain, client_email, webroot_path, dry_run):
    _logger.info(locals())
    out = generate_certificate(custom_domain, client_email, webroot_path, dry_run)
    _logger.info(out)
    if not out['status']:
        _logger.info("Certificate generation failed", out['stderr'])
        exit(1)
    else:
        _logger.info(out['stdout'], out['stderr'])

def main_remove(custom_domain, module_path):
    _logger.info('-'*10, custom_domain, module_path, '-'*10)
    tele_saas_data = read_path_saas_conf(module_path)
    docker_vhosts = os.path.join(tele_saas_data, "docker_vhosts")
    try:
        remove_vhost(custom_domain, docker_vhosts)
        return { "status": True,"message":True }
    except Exception as e:
        return { "status": False,"message":"Error %r"%e }

def main_add(subdomain, custom_domain, ssl_flag, module_path):
    _logger.info(locals())
    regex = re.compile("^((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}$")
    if not re.search(regex,custom_domain):
        _logger.info("Invalid Domain %r"%custom_domain)
        return {
                'status': False,
                'message': "Invalid Domain %r. Try replacing underscore with hypen & avoid any other special characters."%custom_domain
                }
    tele_saas_data = read_path_saas_conf(module_path)
    try:
        if check_ips(custom_domain, subdomain):
            tele_backend, longpolling_backend = grep_backends_from_conf(os.path.join(tele_saas_data, "docker_vhosts"), subdomain)
            _logger.info("%r %r"%(tele_backend, longpolling_backend))
            create_vhost_http(subdomain, custom_domain, tele_backend, longpolling_backend, docker_vhosts=os.path.join(tele_saas_data, "docker_vhosts"))
            _logger.info("HTTP Createf for %s"%custom_domain)
            #create_vhost(subdomain, custom_domain, tele_backend, longpolling_backend, docker_vhosts=os.path.join(tele_saas_data, "docker_vhosts"))
            if ssl_flag:
                _logger.info("SSL to be done for %s"%custom_domain)
                run_certbot(custom_domain, client_email=CLIENT_EMAIL, webroot_path=WEBROOT_PATH, dry_run=False)
                _logger.info("SSL generated")
                create_vhost_https(subdomain, custom_domain, tele_backend, longpolling_backend, docker_vhosts=os.path.join(tele_saas_data, "docker_vhosts"))
                _logger.info("Create HHTPS vhost")
                #create_vhost_redirect(custom_domain, docker_vhosts=os.path.join(tele_saas_data, "docker_vhosts"))
            return {
                'status': True,
                'message': "Certs generate successfully"
            }
    except Exception as e:
        return {
            'status': False,
            'message': "%r"%e
        }
 
if __name__ == '__main__':

    """
    USAGE: 
    Just call main() function with params:
    subdomain: existing domain
    custom_domain: new domain
    ssl_flag: to notify if ssl certs are already present
    """

    subdomain = "trial_test_4.saas.tele.studio"
    custom_domain = "gc-new.saas.tele.studio"

    main_add(subdomain=subdomain, custom_domain=custom_domain, ssl_flag=True, module_path="/opt/tele14/tele_applets/tele_saas_kit/")
    
    # EVERTHING UNDERNEATH THIS IS FOR TESTING
    #tele_saas_data = os.getcwd()
    #tele_backend, longpolling_backend = grep_backends_from_conf(tele_saas_data, "test.tele-saas.tele.studio")
    # run_certbot(domain_name="domain.com", client_email="abc@domain.com", webroot_path="/usr/share/nginx/html/", dry_run=True)
    #create_vhost("test.tele-saas.tele.studio", "domain.ml", tele_backend, longpolling_backend, docker_vhosts=tele_saas_data, ssl_flag=True)
    #remove_vhost("test.abc.com", docker_vhosts="")
