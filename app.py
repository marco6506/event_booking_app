@app.errorhandler(401)
def unauthorized(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Non autorizzato'}), 401
    return redirect(url_for('login'))

@app.errorhandler(403)
def forbidden(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Accesso negato'}), 403
    flash('Accesso negato.', 'danger')
    return redirect(url_for('calendar_view'))

@app.route('/api/seats/<int:event_id>')
@login_required
def api_seats(event_id):
    evento = db.session.get(Evento, event_id)
    if not evento:
        return jsonify({'error': 'Evento non trovato'}), 404

    posti = Posto.query.options(
        joinedload(Posto.prenotazione).joinedload(Prenotazione.utente)
    ).filter_by(evento_id=event_id).order_by(Posto.fila, Posto.colonna).all()

    corridoio_colonne = []
    if evento and evento.corridoio_colonne:
        try:
            corridoio_colonne = [int(x.strip()) for x in evento.corridoio_colonne.split(',') if x.strip()]
        except ValueError:
            corridoio_colonne = []

    corridoio_file = []
    if evento and evento.corridoio_file:
        try:
            corridoio_file = [int(x.strip()) for x in evento.corridoio_file.split(',') if x.strip()]
        except ValueError:
            corridoio_file = []

    result = []
    for p in posti:
        item = {
            'id': p.id,
            'fila': p.fila,
            'colonna': p.colonna,
            'stato': p.stato,
            'numero_posto': p.numero_posto,
            'utente_id': None,
            'corridoio_colonne': corridoio_colonne,
            'corridoio_file': corridoio_file
        }
        if p.prenotazione:
            item['utente_id'] = p.prenotazione.utente_id
            item['is_mio'] = (p.prenotazione.utente_id == current_user.id)
            item['prenotazione_id'] = p.prenotazione.id
            item['nome_prenotazione'] = p.prenotazione.nome_prenotazione or p.prenotazione.utente.nome_cognome
            item['utente_nome'] = p.prenotazione.utente.nome_cognome
            if current_user.is_admin():
                item['utente'] = p.prenotazione.utente.nome_cognome
        else:
            item['is_mio'] = False
        result.append(item)
    return jsonify(result)
