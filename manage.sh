NGINX_PREFIX="/home/$USER/smrtlink-proxy/nginx"
SMRT_ROOT="/home/$USER/smrtlink-container/smrtlink"

build() {
    singularity build \
        --fakeroot \
        --force \
        --build-arg nginx_prefix=$NGINX_PREFIX \
        --build-arg smrt_root=$SMRT_ROOT \
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
web() { curl -s -o /dev/null localhost:8088; }
http() { curl -s -k http://localhost:9092/status > /dev/null; }
https() { curl -s -k https://localhost:8244/SMRTLink/1.0.0/status > /dev/null; }

shell() {
    ! container && echo "The container is not running." && return 1
    singularity shell instance://proxy
}

reload() {
    ! container && echo "The container is not running." && return 1
    singularity exec instance://proxy \
        nginx -p $NGINX_PREFIX -s reload
}

config() {
    ! container && echo "The container is not running." && return 1
    singularity exec instance://proxy \
        nginx -p $NGINX_PREFIX -T
}

test_config() {
    ! container && echo "The container is not running." && return 1
    singularity exec instance://proxy \
        nginx -p $NGINX_PREFIX -t
}