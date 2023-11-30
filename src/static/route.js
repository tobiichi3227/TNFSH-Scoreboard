var route = new function() {
    this.session_id = null;
    this.curr_url = null;
    this.prev_url = null;
    this.main_navbar = null;

    this.init = function() {
        let session_id = $('#indexjs').attr('session_id');
        this.main_navbar = $('.main-navbar');

        this.main_navbar.find('.nav-link.logout').on('click', event => {
            $.post('/board/be/login', {
                reqtype: 'logout',
                session_id: session_id,
            }, res => {
                location.href = '/board/info';
            })
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
            $.get('/board/be/' + req_path, args, res => {
                routerView.html(res).ready(() => {
                    route.main_navbar.find('li').find('a.active').removeClass('active');
                    route.main_navbar.find(`li.${page}`).find('a').addClass('active');

                    if (typeof(init) == 'function') {
                        init();
                    }

                    routerView.find('a').each((_, element) => {
                        $(element).on('click', (event) => {
                            event.preventDefault();
                            history.pushState(null, '', $(element).attr('href'))
                            PoPState()
                        })
                    })
                });
            })
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
