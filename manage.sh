build() {
    singularity build --fakeroot \
        alpine_nginx.sif alpine_nginx.def
}

start() {
    singularity instance start \ 
        alpine_nginx.sif proxy
}

stop() {
    singularity instance stop proxy
}