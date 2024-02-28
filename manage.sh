REPO_ROOT="/home/$USER/smrtlink-proxy"
SMRT_ROOT="/home/$USER/smrtlink-container/smrtlink"
PROXY_CONF="/etc/nginx/proxy.conf"

NGINX_CMD="nginx -p $REPO_ROOT/nginx -c /etc/nginx/unprivileged.conf"

build_configs() {
    for t in "$REPO_ROOT"/templates/*; do
        template=/tmp/$(basename "$t").conf
        cp "$t" $template
        for var in REPO_ROOT SMRT_ROOT PROXY_CONF; do
            sed -i "s|$var|${!var}|g" $template
        done
    done
}

build() {
    build_configs
    singularity build \
        --fakeroot --force \
        --build-arg nginx_cmd="$NGINX_CMD" \
        alpine_nginx.sif alpine_nginx.def
}

start() {
    container && echo "The container is already running." && return 1
    singularity instance start alpine_nginx.sif proxy
}

stop() {
    ! container && echo "The container is not running." && return 1
    singularity instance stop proxy
}

container() { singularity instance list | awk 'NR>1 {print $1}' | grep -q proxy; }
sl() { curl -s -o /dev/null http://localhost:9091/status; }
web() { curl -s -o /dev/null localhost:8088; }
http() {
    ! container && echo "The container is not running." && return 1
    ! sl && echo "SMRT Link is not accessible." && return 1
    test "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:9092/status)" -eq 200;
}
https() { 
    ! container && echo "The container is not running." && return 1
    ! sl && echo "SMRT Link is not accessible." && return 1
    test "$(curl -s -k -o /dev/null -w '%{http_code}' https://localhost:8244/SMRTLink/1.0.0/status)" -eq 401; 
}

shell() {
    ! container && echo "The container is not running." && return 1
    singularity shell instance://proxy
}

get_config() {
    ! container && echo "The container is not running." && return 1
    singularity exec instance://proxy eval "$NGINX_CMD -T"
}

test_templates() {
    ! container && echo "The container is not running." && return 1
    ( PROXY_CONF=/tmp/proxy.conf; build_configs )
    singularity exec instance://proxy nginx -p $REPO_ROOT/nginx -t -c /tmp/unprivileged.conf
}