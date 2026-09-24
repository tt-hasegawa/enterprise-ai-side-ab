const ReservationForm = {
    template: `
        <div class="row justify-content-center">
            <div class="col-md-8">
                <a href="#" class="btn btn-outline-secondary mb-3" @click="$root.navigate('/')">&larr; {{ $t('common.back') }}</a>
                <h2 class="mb-4">{{ $t('reservation.title') }}</h2>
                <div v-if="!store.user" class="alert alert-warning">
                    <a href="#" @click="$root.navigate('/login')">{{ $t('auth.login_title') }}</a>
                </div>
                <div v-else>
                    <div v-if="facility" class="card mb-4">
                        <div class="card-body">
                            <h5>{{ facility.name }}</h5>
                            <p class="text-muted">{{ facility.address }}</p>
                            <p><strong>{{ $t('facility.price') }}:</strong> {{ facility.price_per_hour.toLocaleString() }}{{ $t('facility.per_hour') }}</p>
                        </div>
                    </div>
                    <form @submit.prevent="handleSubmit">
                        <div class="mb-3">
                            <label class="form-label">{{ $t('reservation.date') }}</label>
                            <input v-model="form.date" type="date" class="form-control" :min="today" required>
                        </div>
                        <div class="row mb-3">
                            <div class="col">
                                <label class="form-label">{{ $t('reservation.start') }}</label>
                                <select v-model="form.start_time" class="form-select" required>
                                    <option v-for="h in hours" :key="h" :value="h + ':00'">{{ h }}:00</option>
                                </select>
                            </div>
                            <div class="col">
                                <label class="form-label">{{ $t('reservation.end') }}</label>
                                <select v-model="form.end_time" class="form-select" required>
                                    <option v-for="h in hours" :key="h" :value="h + ':00'" :disabled="h <= startHour">{{ h }}:00</option>
                                </select>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">{{ $t('reservation.people') }}</label>
                            <input v-model.number="form.people" type="number" class="form-control" min="1" :max="facility ? facility.capacity : 100" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">{{ $t('reservation.purpose') }}</label>
                            <input v-model="form.purpose" class="form-control" :placeholder="$t('reservation.purpose_placeholder')">
                        </div>
                        <div v-if="totalAmount > 0" class="alert alert-info">
                            <strong>{{ $t('reservation.total_amount') }}:</strong> {{ totalAmount.toLocaleString() }}{{ $t('facility.per_hour') }}
                        </div>
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <button type="submit" class="btn btn-primary btn-lg">{{ $t('reservation.create') }}</button>
                    </form>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            facility: null,
            form: { date: new Date().toISOString().split('T')[0], start_time: '10:00', end_time: '12:00', people: 1, purpose: '' },
            error: null,
            hours: Array.from({ length: 12 }, (_, i) => i + 9)
        };
    },
    computed: {
        today() { return new Date().toISOString().split('T')[0]; },
        startHour() { return parseInt(this.form.start_time); },
        totalAmount() {
            if (!this.facility) return 0;
            const start = parseInt(this.form.start_time);
            const end = parseInt(this.form.end_time);
            if (end <= start) return 0;
            return (end - start) * this.facility.price_per_hour;
        }
    },
    methods: {
        async fetchFacility() {
            try {
                const id = this.$root.getParam('id');
                if (!id) return;
                const lang = i18n.global.locale;
                this.facility = await apiFetch('/api/facilities/' + id + '?lang=' + lang);
            } catch (e) { console.error(e); }
        },
        async handleSubmit() {
            if (!this.facility) return;
            try {
                const result = await apiFetch('/api/reservations', {
                    method: 'POST',
                    body: JSON.stringify({
                        facility_id: this.facility.id,
                        reserved_date: this.form.date,
                        start_time: this.form.start_time,
                        end_time: this.form.end_time,
                        number_of_people: this.form.people,
                        purpose: this.form.purpose
                    })
                });
                this.$root.navigate('/payment?id=' + result.id);
            } catch (e) {
                this.error = e.detail || this.$t('common.error');
            }
        }
    },
    mounted() {
        this.fetchFacility();
    },
    watch: {
        '$root.currentRoute'() {
            this.fetchFacility();
        }
    }
};
