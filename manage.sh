REPO_ROOT="/home/$USER/smrtlink-proxy"
SMRT_ROOT="/home/$USER/smrtlink-container/smrtlink"
NGINX_CMD="nginx -p $REPO_ROOT/nginx -c /etc/nginx/unprivileged.conf"

build() {
    singularity build \
        --fakeroot --force \
        --build-arg repo_root="$REPO_ROOT" \
        --build-arg smrt_root="$SMRT_ROOT" \
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
web() { curl -s localhost:8088 > /dev/null; }
http() { curl -s http://localhost:9092/status > /dev/null; }
https() { test "$(curl -s -k -o /dev/null -w '%{http_code}' https://localhost:8244/SMRTLink/1.0.0/status)" -eq 401; }

shell() {
    ! container && echo "The container is not running." && return 1
    singularity shell instance://proxy
}

reload() {
    ! container && echo "The container is not running." && return 1
    singularity exec instance://proxy eval "$NGINX_CMD -s reload"
}

config() {
    ! container && echo "The container is not running." && return 1
    singularity exec instance://proxy eval "$NGINX_CMD -T"
}