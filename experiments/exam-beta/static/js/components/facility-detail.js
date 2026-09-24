const FacilityDetail = {
    template: `
        <div>
            <a href="#" class="btn btn-outline-secondary mb-3" @click="$root.navigate('/')">&larr; {{ $t('common.back') }}</a>
            <div v-if="loading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else-if="facility">
                <h2>{{ facility.name }}</h2>
                <span class="badge bg-secondary mb-3">{{ typeLabel(facility.type) }}</span>
                <p><strong>{{ $t('facility.type') }}:</strong> {{ facility.address }}</p>
                <p><strong>{{ $t('facility.capacity') }}:</strong> {{ facility.capacity }}{{ $t('reservation.person') }}</p>
                <p><strong>{{ $t('facility.price') }}:</strong> {{ facility.price_per_hour.toLocaleString() }}{{ $t('facility.per_hour') }}</p>
                <p v-if="facility.description">{{ facility.description }}</p>

                <hr>
                <h4>{{ $t('facility.availability') }}</h4>
                <div class="mb-3">
                    <label class="form-label">{{ $t('reservation.date') }}</label>
                    <input v-model="date" type="date" class="form-control w-auto" :min="today" @change="fetchAvailability">
                </div>
                <div v-if="slots.length > 0" class="row">
                    <div v-for="slot in slots" :key="slot.time" class="col-4 col-md-2 mb-2">
                        <div :class="['btn', slot.available ? 'btn-outline-success' : 'btn-outline-secondary disabled', 'w-100']">
                            {{ slot.time }}<br>
                            <small>{{ slot.available ? $t('facility.available') : $t('facility.unavailable') }}</small>
                        </div>
                    </div>
                </div>

                <hr>
                <a href="#" class="btn btn-primary btn-lg" @click="$root.navigate('/reserve?id=' + facility.id)">
                    {{ $t('facility.reserve') }}
                </a>
            </div>
            <div v-else class="alert alert-danger">{{ $t('common.error') }}</div>
        </div>
    `,
    data() {
        return {
            facility: null,
            loading: true,
            date: new Date().toISOString().split('T')[0],
            slots: []
        };
    },
    computed: {
        today() { return new Date().toISOString().split('T')[0]; }
    },
    methods: {
        typeLabel(type) {
            const labels = { gym: this.$t('facility.gym'), meeting_room: this.$t('facility.meeting_room'), pool: this.$t('facility.pool') };
            return labels[type] || type;
        },
        async fetchFacility() {
            try {
                const id = this.$root.getParam('id');
                if (!id) { this.loading = false; return; }
                const lang = i18n.global.locale;
                this.facility = await apiFetch('/api/facilities/' + id + '?lang=' + lang);
                await this.fetchAvailability();
            } catch (e) {
                console.error(e);
            } finally {
                this.loading = false;
            }
        },
        async fetchAvailability() {
            if (!this.date || !this.facility) return;
            try {
                const result = await apiFetch('/api/facilities/' + this.facility.id + '/availability?date=' + this.date);
                this.slots = result.slots || [];
            } catch (e) {
                console.error(e);
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
