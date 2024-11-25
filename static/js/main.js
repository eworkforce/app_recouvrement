document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des graphiques si les données sont disponibles
    if (graphData) {
        Plotly.newPlot('statusChart', JSON.parse(graphData.status));
        Plotly.newPlot('evolutionChart', JSON.parse(graphData.evolution));
    }

    function loadClients() {
        fetch('/clients')
            .then(response => response.json())
            .then(clients => {
                const tbody = document.getElementById('clientsTableBody');
                tbody.innerHTML = '';
                clients.forEach(client => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${client.id}</td>
                        <td>${client.nom}</td>
                        <td>${client.email}</td>
                        <td>${client.telephone}</td>
                    `;
                    tbody.appendChild(tr);
                });
            })
            .catch(error => console.error('Erreur:', error));
    }

    function loadFactures() {
        fetch('/factures')
            .then(response => response.json())
            .then(factures => {
                const tbody = document.getElementById('facturesTableBody');
                tbody.innerHTML = '';
                factures.forEach(facture => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${facture.numero}</td>
                        <td>${facture.client_nom}</td>
                        <td>${facture.montant.toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'})}</td>
                        <td>${formatDate(facture.date_emission)}</td>
                        <td>${formatDate(facture.date_echeance)}</td>
                        <td>
                            <div class="dropdown">
                                <button class="btn btn-sm dropdown-toggle badge bg-${getStatusColor(facture.statut)}" 
                                        type="button" data-bs-toggle="dropdown">
                                    ${facture.statut}
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="#" onclick="updateFactureStatus(${facture.id}, 'En attente')">En attente</a></li>
                                    <li><a class="dropdown-item" href="#" onclick="updateFactureStatus(${facture.id}, 'Payée')">Payée</a></li>
                                    <li><a class="dropdown-item" href="#" onclick="updateFactureStatus(${facture.id}, 'En retard')">En retard</a></li>
                                </ul>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            })
            .catch(error => console.error('Erreur:', error));
    }

    // Navigation
    document.querySelectorAll('.nav-link[data-section]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Mise à jour des classes actives
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Affichage de la section
            const targetSection = this.dataset.section;
            document.querySelectorAll('section').forEach(s => s.classList.remove('active-section'));
            document.getElementById(targetSection).classList.add('active-section');
            
            // Recharger les données si nécessaire
            if (targetSection === 'clients') {
                loadClients();
            } else if (targetSection === 'factures') {
                loadFactures();
            } else if (targetSection === 'exports') {
                loadExports();
            }
        });
    });

    // Chargement des données initiales
    loadClients();
    loadFactures();

    // Gestionnaire pour le formulaire client
    document.getElementById('addClientForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const clientData = {
            nom: document.getElementById('nom').value,
            email: document.getElementById('email').value,
            telephone: document.getElementById('telephone').value
        };

        fetch('/clients', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(clientData)
        })
        .then(response => response.json())
        .then(data => {
            // Fermer le modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addClientModal'));
            modal.hide();
            
            // Recharger les données
            loadClients();
            document.getElementById('addClientForm').reset();
            
            // Notification
            showNotification('Client ajouté avec succès');
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur lors de l\'ajout du client', 'error');
        });
    });

    // Gestionnaire pour le formulaire facture
    document.getElementById('factureForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const factureData = {
            client_id: document.getElementById('client').value,
            numero: document.getElementById('numero').value,
            montant: parseFloat(document.getElementById('montant').value),
            date_emission: document.getElementById('date_emission').value,
            date_echeance: document.getElementById('date_echeance').value
        };

        fetch('/factures', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(factureData)
        })
        .then(response => response.json())
        .then(data => {
            // Fermer le modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('factureModal'));
            modal.hide();
            
            // Recharger les données
            loadFactures();
            document.getElementById('factureForm').reset();
            
            // Recharger les graphiques
            window.location.reload();
            
            // Notification
            showNotification('Facture ajoutée avec succès');
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur lors de l\'ajout de la facture', 'error');
        });
    });

    // Gestionnaire pour le formulaire de filtres
    document.getElementById('filterForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const params = new URLSearchParams();
        
        for (let pair of formData.entries()) {
            if (pair[1]) {  // Ne pas ajouter les paramètres vides
                params.append(pair[0], pair[1]);
            }
        }
        
        window.location.href = '/?' + params.toString();
    });

    // Gestion de l'importation de données
    document.querySelectorAll('.import-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const fileInput = this.querySelector('input[type="file"]');
            const file = fileInput.files[0];
            const type = this.dataset.type;
            
            if (!file) {
                showNotification('Veuillez sélectionner un fichier', 'error');
                return;
            }
            
            // Vérification de l'extension
            if (!file.name.endsWith('.csv')) {
                showNotification('Le fichier doit être au format CSV', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Envoi du fichier
            fetch(`/import/${type}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    
                    // Affichage de l'aperçu
                    if (data.preview && data.preview.length > 0) {
                        const preview = document.getElementById('importPreview');
                        const header = document.getElementById('previewHeader');
                        const body = document.getElementById('previewBody');
                        
                        // En-têtes
                        const columns = Object.keys(data.preview[0]);
                        header.innerHTML = `<tr>${columns.map(col => `<th>${col}</th>`).join('')}</tr>`;
                        
                        // Données
                        body.innerHTML = data.preview.map(row => 
                            `<tr>${columns.map(col => `<td>${row[col]}</td>`).join('')}</tr>`
                        ).join('');
                        
                        preview.style.display = 'block';
                    }
                    
                    // Masquer les erreurs
                    document.getElementById('importErrors').style.display = 'none';
                    
                    // Recharger les données
                    loadClients();
                    loadFactures();
                    
                    // Réinitialiser le formulaire
                    fileInput.value = '';
                } else {
                    // Affichage des erreurs
                    const errorsDiv = document.getElementById('importErrors');
                    errorsDiv.innerHTML = `
                        <h6>Erreurs de validation :</h6>
                        <ul>
                            ${data.errors.map(error => `<li>${error}</li>`).join('')}
                        </ul>
                    `;
                    errorsDiv.style.display = 'block';
                    
                    // Masquer l'aperçu
                    document.getElementById('importPreview').style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                showNotification('Erreur lors de l\'importation', 'error');
            });
        });
    });

    // Gestion de la configuration des exports
    function loadExportConfig() {
        fetch('/export-config')
            .then(response => response.json())
            .then(config => {
                // Configuration quotidienne
                document.querySelector('form[data-type="daily"] input[type="checkbox"]').checked = config.daily.enabled;
                document.querySelector('form[data-type="daily"] select[name="hour"]').value = config.daily.hour;
                document.querySelector('form[data-type="daily"] select[name="minute"]').value = config.daily.minute;

                // Configuration hebdomadaire
                document.querySelector('form[data-type="weekly"] input[type="checkbox"]').checked = config.weekly.enabled;
                document.querySelector('form[data-type="weekly"] select[name="day"]').value = config.weekly.day;
                document.querySelector('form[data-type="weekly"] select[name="hour"]').value = config.weekly.hour;
                document.querySelector('form[data-type="weekly"] select[name="minute"]').value = config.weekly.minute;

                // Configuration mensuelle
                document.querySelector('form[data-type="monthly"] input[type="checkbox"]').checked = config.monthly.enabled;
                document.querySelector('form[data-type="monthly"] select[name="day"]').value = config.monthly.day;
                document.querySelector('form[data-type="monthly"] select[name="hour"]').value = config.monthly.hour;
                document.querySelector('form[data-type="monthly"] select[name="minute"]').value = config.monthly.minute;
            })
            .catch(error => console.error('Erreur:', error));
    }

    // Gestion des formulaires de configuration
    document.querySelectorAll('.export-config-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const type = this.dataset.type;
            const data = {
                enabled: this.querySelector('input[type="checkbox"]').checked,
                hour: parseInt(this.querySelector('select[name="hour"]').value),
                minute: parseInt(this.querySelector('select[name="minute"]').value)
            };

            // Ajout du jour pour les exports hebdomadaires et mensuels
            if (type === 'weekly' || type === 'monthly') {
                data.day = this.querySelector('select[name="day"]').value;
            }

            fetch(`/export-config/${type}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showNotification('Configuration sauvegardée', 'success');
                } else {
                    showNotification('Erreur lors de la sauvegarde', 'error');
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                showNotification('Erreur lors de la sauvegarde', 'error');
            });
        });
    });

    loadExportConfig();

    function updateFactureStatus(factureId, newStatus) {
        fetch(`/factures/${factureId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        })
        .then(response => response.json())
        .then(data => {
            showNotification('Statut mis à jour avec succès');
            window.location.reload();
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur lors de la mise à jour du statut', 'error');
        });
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    }

    function getStatusColor(status) {
        switch(status) {
            case 'Payée':
                return 'success';
            case 'En attente':
                return 'warning';
            case 'En retard':
                return 'danger';
            default:
                return 'secondary';
        }
    }

    function showNotification(message, type = 'success') {
        // Créer l'élément de notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification`;
        notification.textContent = message;
        
        // Ajouter au document
        document.body.appendChild(notification);
        
        // Supprimer après 3 secondes
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Chargement des exports
    function loadExports() {
        fetch('/exports/latest')
            .then(response => response.json())
            .then(files => {
                const tbody = document.getElementById('exportsTableBody');
                tbody.innerHTML = '';
                
                if (files.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" class="text-center">Aucun export disponible</td></tr>';
                    return;
                }
                
                files.forEach(file => {
                    const tr = document.createElement('tr');
                    const size = (file.size / 1024).toFixed(2); // Conversion en KB
                    tr.innerHTML = `
                        <td>${file.name}</td>
                        <td>${file.date}</td>
                        <td>${size} KB</td>
                        <td>
                            <a href="/exports/download/${file.name}" class="btn btn-sm btn-success">
                                <i class="bi bi-download"></i> Télécharger
                            </a>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            })
            .catch(error => {
                console.error('Erreur:', error);
                const tbody = document.getElementById('exportsTableBody');
                tbody.innerHTML = '<tr><td colspan="4" class="text-center text-danger">Erreur lors du chargement des exports</td></tr>';
            });
    }
});
