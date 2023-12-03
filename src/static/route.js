function sameOrigin(a, b) {
    // https://stackoverflow.com/questions/31374766/javascript-how-to-check-if-a-url-is-same-origin-as-current-page
    const urlA = new URL(a);
    const urlB = new URL(b);
    return urlA.origin === urlB.origin;
}

function get_form_data(obj) {
    const fd = new FormData();
    for (let i in obj) {
        append_form_data(obj[i], fd, i)
    }

    return fd
}

function append_form_data(data, form_data, key) {
    if ((typeof data === 'object' && data !== null && !(data instanceof File)) || Array.isArray(data)) {
        for (const i in data) {
            if ((typeof data[i] === 'object' && data[i] !== null) || Array.isArray(data[i])) {
                append_form_data(data[i], form_data, key + `[${i}]`)
            } else {
                form_data.append(key + `[${i}]`, data[i])
            }
        }
    } else {
        form_data.append(key, data)
    }
}

function post(url, form_data) {
    let res = fetch(url, {
        method: 'POST',
        body: get_form_data(form_data)
    });

    return res;
}

async function get(url) {
    let res = await fetch(url);

    return res;
}

var route = new function() {
    this.session_id = null;
    this.curr_url = null;
    this.prev_url = null;
    this.main_navbar = null;

    this.init = function() {
        let session_id = $('#indexjs').attr('session_id');
        this.main_navbar = $('.main-navbar');

        this.main_navbar.find('.nav-link.logout').on('click', event => {
            post('/board/be/login', {
                reqtype: 'logout',
                session_id: session_id,
            }).then(_ => {
                location.href = '/board/info/';
            });
        })

        if (session_id != '') {
            this.session_id = parseInt(session_id);
            this.main_navbar.find('.nav-link.logout').show();
        } else {
            this.main_navbar.find('.nav-link.login').show();
        }

        this.update(0);
    }

    this.go = (url) => {
        window.history.pushState(null, document.title, url);
        this.update(1);
    }

    this.reload = () => {
        this.update(1);
    }

    this.update = function(mode) {
        function PoPState() {
            this.prev_url = location.href;
            let parts = location.href.split('/');
            let page = parts[4];
            if (page == 'index') {
                page = 'info';
            }

            let req_path = parts[4];
            for (let i = 5; i < parts.length-1; i++) {
                req_path += `/${parts[i]}`;
            }

            let args = '';
            parts = parts[parts.length - 1].match(/\?([^#]+)/);
            if (parts == null) {
                args = `cache=${new Date().getTime()}`;
            } else {
                args = parts[1] + `&cache=${new Date().getTime()}`
            }
            

            let request_url = `/board/be/${req_path}?${args}`;
            get(request_url).then(response => {
                return response.text();
            }).then(res => {
                routerView.html(res).ready(() => {
                    route.main_navbar.find('li').find('a.active').removeClass('active');
                    route.main_navbar.find(`li.${page}`).find('a').addClass('active');

                    if (typeof(init) == 'function') {
                        init();
                    }

                    routerView.find('a').each((_, element) => {
                        let j_element = $(element);
                        j_element.on('click', (event) => {
                            if (sameOrigin(j_element.attr('href'), location.href)) {
                                event.preventDefault();
                                history.pushState(null, '', j_element.attr('href'))
                                PoPState()
                            }
                        })
                    })
                });

            });
        }

        var routerView = $('#routerView');

        if (mode == 1) {
            PoPState();
            return;
        }

        window.addEventListener('DOMContentLoaded', onLoad);
        document.getElementById('routerView').addEventListener('DOMContentLoaded', onLoad);
        window.addEventListener('popstate', PoPState);

        function onLoad() {
            PoPState();
            let links = document.querySelectorAll('li a[href]');
            links.forEach(link => {
                link.addEventListener('click', event => {
                    event.preventDefault();

                    history.pushState(null, '', link.getAttribute('href'))
                    PoPState()
                })
            })
        }

        onLoad()
    }
}