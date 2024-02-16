NGINX_PREFIX="/home/$USER/smrtlink-proxy/nginx"

build() {
    singularity build \
        --fakeroot \
        --force \
        --build-arg nginx_prefix=$NGINX_PREFIX \
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

container() { singularity instance list | grep -q proxy; }
web() { curl -s -o /dev/null localhost:8088; }

shell() {
    ! container && echo "The container is not running." && return 1
    singularity shell instance://proxy
}

swap_config() {
    [ -z $1 ] && echo "Usage: set_config <path_to_config>" && return 1
    [ ! -f $1 ] && echo "File not found: $1. File must be in your home directory, or else built into the container." && return
    # Test the configuration
    singularity exec instance://proxy \
        nginx -p $NGINX_PREFIX -t -c $1
    # If the test is successful, set the configuration
    if [ $? -eq 0 ]; then
        singularity exec instance://proxy \
            nginx -p $NGINX_PREFIX -c $1
    else
        echo "Nginx configuration test failed"
    fi
}