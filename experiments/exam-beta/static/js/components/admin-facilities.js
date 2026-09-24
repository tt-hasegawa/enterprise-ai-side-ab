const AdminFacilities = {
    template: `
        <div>
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>{{ $t('admin.facilities') }}</h2>
                <div class="btn-group">
                    <button class="btn btn-outline-primary active">{{ $t('admin.facilities') }}</button>
                    <button class="btn btn-outline-primary" @click="$root.navigate('/admin/reservations')">{{ $t('admin.reservations') }}</button>
                </div>
            </div>
            <div v-if="!store.user || store.user.role !== 'staff'" class="alert alert-danger">
                {{ $t('common.error') }}
            </div>
            <div v-else>
                <button class="btn btn-primary mb-3" @click="showForm = !showForm">
                    {{ $t('admin.add_facility') }}
                </button>
                <div v-if="showForm" class="card mb-4">
                    <div class="card-body">
                        <form @submit.prevent="addFacility">
                            <div class="mb-2">
                                <input v-model="newFacility.name" class="form-control" placeholder="施設名" required>
                            </div>
                            <div class="mb-2">
                                <select v-model="newFacility.type" class="form-select" required>
                                    <option value="gym">{{ $t('facility.gym') }}</option>
                                    <option value="meeting_room">{{ $t('facility.meeting_room') }}</option>
                                    <option value="pool">{{ $t('facility.pool') }}</option>
                                </select>
                            </div>
                            <div class="mb-2">
                                <input v-model="newFacility.address" class="form-control" placeholder="所在地" required>
                            </div>
                            <div class="row mb-2">
                                <div class="col">
                                    <input v-model.number="newFacility.capacity" type="number" class="form-control" placeholder="収容人数">
                                </div>
                                <div class="col">
                                    <input v-model.number="newFacility.price_per_hour" type="number" class="form-control" placeholder="料金/時間">
                                </div>
                            </div>
                            <div class="mb-2">
                                <textarea v-model="newFacility.description" class="form-control" placeholder="説明"></textarea>
                            </div>
                            <button type="submit" class="btn btn-success">{{ $t('common.submit') }}</button>
                        </form>
                    </div>
                </div>

                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>施設名</th>
                            <th>{{ $t('facility.type') }}</th>
                            <th>{{ $t('facility.capacity') }}</th>
                            <th>{{ $t('facility.price') }}</th>
                            <th>{{ $t('admin.delete') }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="f in facilities" :key="f.id">
                            <td>{{ f.id }}</td>
                            <td>{{ f.name }}</td>
                            <td>{{ typeLabel(f.type) }}</td>
                            <td>{{ f.capacity }}</td>
                            <td>{{ f.price_per_hour.toLocaleString() }}{{ $t('facility.per_hour') }}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-danger" @click="deleteFacility(f.id)">{{ $t('admin.delete') }}</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `,
    data() {
        return {
            facilities: [],
            showForm: false,
            newFacility: { name: '', type: 'gym', address: '', capacity: 30, price_per_hour: 1000, description: '' }
        };
    },
    methods: {
        typeLabel(type) {
            const labels = { gym: this.$t('facility.gym'), meeting_room: this.$t('facility.meeting_room'), pool: this.$t('facility.pool') };
            return labels[type] || type;
        },
        async fetchFacilities() {
            try {
                const result = await apiFetch('/api/facilities');
                this.facilities = result.items;
            } catch (e) { console.error(e); }
        },
        async addFacility() {
            try {
                await apiFetch('/api/facilities', {
                    method: 'POST',
                    body: JSON.stringify(this.newFacility)
                });
                this.showForm = false;
                this.newFacility = { name: '', type: 'gym', address: '', capacity: 30, price_per_hour: 1000, description: '' };
                this.fetchFacilities();
            } catch (e) { alert(e.detail || this.$t('common.error')); }
        },
        async deleteFacility(id) {
            if (!confirm(this.$t('admin.confirm_delete'))) return;
            try {
                await apiFetch('/api/facilities/' + id, { method: 'DELETE' });
                this.fetchFacilities();
            } catch (e) { alert(e.detail || this.$t('common.error')); }
        }
    },
    mounted() {
        this.fetchFacilities();
    },
    watch: {
        '$root.currentRoute'() {
            this.fetchFacilities();
        }
    }
};
