const AdminReservations = {
    template: `
        <div>
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>{{ $t('admin.reservations') }}</h2>
                <div class="btn-group">
                    <button class="btn btn-outline-primary" @click="$root.navigate('/admin/facilities')">{{ $t('admin.facilities') }}</button>
                    <button class="btn btn-outline-primary active">{{ $t('admin.reservations') }}</button>
                </div>
            </div>
            <div v-if="!store.user || store.user.role !== 'staff'" class="alert alert-danger">
                {{ $t('common.error') }}
            </div>
            <div v-else>
                <div v-if="loading" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status"></div>
                </div>
                <div v-else-if="reservations.length === 0" class="alert alert-info">
                    {{ $t('reservation.no_reservations') }}
                </div>
                <table v-else class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>{{ $t('auth.username') }}</th>
                            <th>施設名</th>
                            <th>{{ $t('reservation.date') }}</th>
                            <th>{{ $t('reservation.start') }}</th>
                            <th>{{ $t('reservation.end') }}</th>
                            <th>{{ $t('facility.status') }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="r in reservations" :key="r.id">
                            <td>{{ r.id }}</td>
                            <td>{{ r.user_id }}</td>
                            <td>{{ r.facility_name || ('#' + r.facility_id) }}</td>
                            <td>{{ r.reserved_date }}</td>
                            <td>{{ r.start_time }}</td>
                            <td>{{ r.end_time }}</td>
                            <td><span :class="['badge', statusBadge(r.status)]">{{ statusLabel(r.status) }}</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `,
    data() {
        return { reservations: [], loading: true };
    },
    methods: {
        statusBadge(status) {
            return { pending: 'bg-warning', confirmed: 'bg-success', cancelled: 'bg-secondary' }[status] || 'bg-secondary';
        },
        statusLabel(status) {
            const labels = {
                pending: this.$t('reservation.status_pending'),
                confirmed: this.$t('reservation.status_confirmed'),
                cancelled: this.$t('reservation.status_cancelled')
            };
            return labels[status] || status;
        },
        async fetchReservations() {
            this.loading = true;
            try {
                const result = await apiFetch('/api/reservations');
                this.reservations = result.items;
            } catch (e) { console.error(e); }
            finally { this.loading = false; }
        }
    },
    mounted() {
        this.fetchReservations();
    },
    watch: {
        '$root.currentRoute'() {
            this.fetchReservations();
        }
    }
};
