from django import template

from waitinglist.forms import WaitingListEntryForm


register = template.Library()


@register.assignment_tag
def waitinglist_entry_form():
    """
    Get a (new) form object to post a new comment.
    
    Syntax::
    
        {% waitinglist_entry_form as [varname] %}
    
    """
    return WaitingListEntryForm()
