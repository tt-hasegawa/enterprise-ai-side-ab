const PaymentPage = {
    template: `
        <div class="row justify-content-center">
            <div class="col-md-6 text-center">
                <a href="#" class="btn btn-outline-secondary mb-3 float-start" @click="goBack">&larr; {{ $t('common.back') }}</a>
                <h2 class="mb-4">{{ $t('payment.title') }}</h2>
                <div v-if="loading" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status"></div>
                </div>
                <div v-else-if="result">
                    <div class="card mb-4">
                        <div class="card-body">
                            <h3 class="text-success">{{ $t('payment.complete') }}</h3>
                            <p class="fs-4">{{ $t('payment.amount') }}: {{ result.amount.toLocaleString() }}{{ $t('facility.per_hour') }}</p>
                            <div v-if="result.qr_code_data" class="my-4">
                                <img :src="result.qr_code_data" alt="QR Code" class="img-fluid" style="max-width: 250px;">
                                <p class="mt-2 text-muted">{{ $t('payment.qr_instruction') }}</p>
                            </div>
                            <p class="text-muted">{{ $t('reservation.status_confirmed') }}</p>
                        </div>
                    </div>
                    <div class="d-flex gap-2 justify-content-center">
                        <a :href="'/api/reservations/' + reservationId + '/pdf'" class="btn btn-primary" target="_blank">
                            {{ $t('reservation.download_pdf') }}
                        </a>
                        <a href="#" class="btn btn-outline-primary" @click="$root.navigate('/reservations')">
                            {{ $t('nav.reservations') }}
                        </a>
                    </div>
                </div>
                <div v-else>
                    <p class="mb-4">{{ $t('payment.amount') }}: <strong class="fs-3">{{ amount.toLocaleString() }}{{ $t('facility.per_hour') }}</strong></p>
                    <button class="btn btn-success btn-lg" @click="processPayment">
                        {{ $t('payment.pay') }}
                    </button>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            reservationId: null,
            amount: 0,
            result: null,
            loading: false
        };
    },
    methods: {
        goBack() {
            if (this.result) {
                this.$root.navigate('/reservations');
            } else {
                this.$root.navigate('/reservation?id=' + this.reservationId);
            }
        },
        async processPayment() {
            this.loading = true;
            try {
                this.result = await apiFetch('/api/payments/' + this.reservationId + '/pay', { method: 'POST' });
            } catch (e) {
                alert(e.detail || this.$t('common.error'));
            } finally {
                this.loading = false;
            }
        },
        async fetchReservation() {
            try {
                const id = this.$root.getParam('id');
                if (!id) return;
                this.reservationId = id;
                const r = await apiFetch('/api/reservations/' + id);
                const fac = await apiFetch('/api/facilities/' + r.facility_id);
                const start = parseInt(r.start_time);
                const end = parseInt(r.end_time);
                this.amount = (end - start) * fac.price_per_hour;

                const payment = await apiFetch('/api/payments/' + id).catch(() => null);
                if (payment && payment.status === 'paid') {
                    this.result = payment;
                }
            } catch (e) { console.error(e); }
        }
    },
    mounted() {
        this.fetchReservation();
    },
    watch: {
        '$root.currentRoute'() {
            this.fetchReservation();
        }
    }
};
