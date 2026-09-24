const ReservationDetail = {
    template: `
        <div class="row justify-content-center">
            <div class="col-md-8">
                <a href="#" class="btn btn-outline-secondary mb-3" @click="$root.navigate('/reservations')">&larr; {{ $t('common.back') }}</a>
                <div v-if="loading" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status"></div>
                </div>
                <div v-else-if="reservation">
                    <h2 class="mb-4">{{ $t('reservation.title') }} #{{ reservation.id }}</h2>
                    <div class="card mb-4">
                        <div class="card-body">
                            <table class="table">
                                <tr>
                                    <th>{{ $t('facility.type') }}</th>
                                    <td>{{ reservation.facility_name || '-' }}</td>
                                </tr>
                                <tr>
                                    <th>{{ $t('reservation.date') }}</th>
                                    <td>{{ reservation.reserved_date }}</td>
                                </tr>
                                <tr>
                                    <th>{{ $t('reservation.start') }}</th>
                                    <td>{{ reservation.start_time }}</td>
                                </tr>
                                <tr>
                                    <th>{{ $t('reservation.end') }}</th>
                                    <td>{{ reservation.end_time }}</td>
                                </tr>
                                <tr>
                                    <th>{{ $t('reservation.people') }}</th>
                                    <td>{{ reservation.number_of_people }}{{ $t('reservation.person') }}</td>
                                </tr>
                                <tr v-if="reservation.purpose">
                                    <th>{{ $t('reservation.purpose') }}</th>
                                    <td>{{ reservation.purpose }}</td>
                                </tr>
                                <tr>
                                    <th>{{ $t('facility.status') }}</th>
                                    <td><span :class="['badge', statusBadge]">{{ statusLabel }}</span></td>
                                </tr>
                                <tr v-if="reservation.payment_status">
                                    <th>{{ $t('payment.title') }}</th>
                                    <td>
                                        <span :class="['badge', reservation.payment_status === 'paid' ? 'bg-success' : 'bg-warning']">
                                            {{ reservation.payment_status === 'paid' ? $t('payment.complete') : $t('payment.unpaid') }}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    <div class="d-flex gap-2">
                        <a v-if="reservation.status === 'pending' || reservation.status === 'confirmed'" href="#" class="btn btn-success" @click="$root.navigate('/payment?id=' + reservation.id)">
                            {{ $t('payment.title') }}
                        </a>
                        <a :href="'/api/reservations/' + reservation.id + '/pdf'" class="btn btn-primary" target="_blank">
                            {{ $t('reservation.download_pdf') }}
                        </a>
                        <button v-if="reservation.status !== 'cancelled'" class="btn btn-danger" @click="cancelReservation">
                            {{ $t('reservation.cancel') }}
                        </button>
                    </div>
                </div>
                <div v-else class="alert alert-danger">{{ $t('common.error') }}</div>
            </div>
        </div>
    `,
    data() {
        return { reservation: null, loading: true };
    },
    computed: {
        statusBadge() {
            return { pending: 'bg-warning', confirmed: 'bg-success', cancelled: 'bg-secondary' }[this.reservation?.status] || 'bg-secondary';
        },
        statusLabel() {
            const labels = {
                pending: this.$t('reservation.status_pending'),
                confirmed: this.$t('reservation.status_confirmed'),
                cancelled: this.$t('reservation.status_cancelled')
            };
            return labels[this.reservation?.status] || this.reservation?.status;
        }
    },
    methods: {
        async fetchReservation() {
            try {
                const id = this.$root.getParam('id');
                if (!id) { this.loading = false; return; }
                this.reservation = await apiFetch('/api/reservations/' + id);
            } catch (e) {
                console.error(e);
            } finally {
                this.loading = false;
            }
        },
        async cancelReservation() {
            if (!confirm(this.$t('reservation.cancel_confirm'))) return;
            try {
                await apiFetch('/api/reservations/' + this.reservation.id, { method: 'DELETE' });
                this.reservation.status = 'cancelled';
            } catch (e) {
                alert(e.detail || this.$t('common.error'));
            }
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
