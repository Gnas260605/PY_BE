from views.ticket_board import render_ticket_board


def render_my_tickets_view() -> None:
    render_ticket_board("Ticket của tôi", default_user_scope=True)
