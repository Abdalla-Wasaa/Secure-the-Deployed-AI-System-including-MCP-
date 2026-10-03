ROLE_MATRIX = {
 'partner': frozenset({'triage','check_stock'}),
 'operations': frozenset({'check_stock','plan_delivery_route'}),
 'admin': frozenset({'check_stock','plan_delivery_route','rights'}),
 'unknown': frozenset(),
}
def allowed(role, action):
    return action in ROLE_MATRIX.get(role, frozenset())
