const app = Vue.createApp({
    data() {
        return {
            store,
            currentRoute: '/',
            currentParams: {},
            loading: false,
            error: null
        };
    },
    computed: {
        currentPage() {
            const routes = {
                '/': 'facility-list',
                '/login': 'login-page',
                '/register': 'register-page',
                '/facility': 'facility-detail',
                '/reserve': 'reservation-form',
                '/reservations': 'reservation-list',
                '/reservation': 'reservation-detail',
                '/payment': 'payment-page',
                '/profile': 'profile-page',
                '/admin/facilities': 'admin-facilities',
                '/admin/reservations': 'admin-reservations'
            };
            const path = this.currentRoute.split('?')[0];
            return routes[path] || 'facility-list';
        },
        currentLangLabel() {
            const labels = { ja: '日本語', en: 'English', zh: '中文' };
            return labels[i18n.global.locale] || '日本語';
        }
    },
    methods: {
        getParam(name) {
            const queryString = this.currentRoute.includes('?') ? this.currentRoute.split('?')[1] : '';
            const params = new URLSearchParams(queryString);
            return params.get(name) || new URLSearchParams(window.location.search).get(name);
        },
        navigate(path) {
            this.currentRoute = path;
            window.scrollTo(0, 0);
        },
        setLanguage(lang) {
            i18n.global.locale = lang;
            localStorage.setItem('lang', lang);
            store.user && (store.user.language = lang);
        },
        async logout() {
            try {
                await apiFetch('/api/auth/logout', { method: 'POST' });
                store.user = null;
                this.navigate('/');
            } catch (e) {
                console.error('Logout failed', e);
            }
        },
        async checkAuth() {
            try {
                const user = await apiFetch('/api/auth/me');
                store.user = user;
                if (user.language && user.language !== i18n.global.locale) {
                    this.setLanguage(user.language);
                }
            } catch (e) {
                store.user = null;
            }
        }
    },
    async mounted() {
        await this.checkAuth();
    }
});

app.component('facility-list', FacilityList);
app.component('facility-detail', FacilityDetail);
app.component('reservation-form', ReservationForm);
app.component('reservation-list', ReservationList);
app.component('reservation-detail', ReservationDetail);
app.component('payment-page', PaymentPage);
app.component('login-page', LoginPage);
app.component('register-page', RegisterPage);
app.component('profile-page', ProfilePage);
app.component('admin-facilities', AdminFacilities);
app.component('admin-reservations', AdminReservations);

app.use(i18n);
app.mount('#app');
