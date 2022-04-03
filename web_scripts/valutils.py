import authutils
import db
import strutils


def validate_add_permission():
    """Check if the user has permission to add projects.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    user = authutils.get_kerberos()
    can_add = authutils.can_add(user)
    if can_add:
        status_messages = []
    else:
        status_messages = ['User is not authorized to add projects!']
    return can_add, status_messages


def validate_project_name_text(name):
    """Check if the project name text is valid.

    Parameters
    ----------
    name : str
        The proposed project name.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    name_ok = len(name) >= 1
    if name_ok:
        status_messages = []
    else:
        status_messages = ['Project name must be non-empty!']
    return name_ok, status_messages


def validate_project_name_available(name):
    """Check if the project name is available.

    Parameters
    ----------
    name : str
        The proposed project name.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    project_id = db.get_project_id(name)
    if project_id:
        return False, ['A project with name "%s" already exists!' % name]
    else:
        return True, []


def validate_project_name(name, previous_name=None):
    """Check if the project name field is valid.

    Parameters
    ----------
    name : str
        The proposed project name.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    name_ok = True
    status_messages = []

    name_text_ok, name_msgs = validate_project_name_text(name)
    name_ok &= name_text_ok
    status_messages.extend(name_msgs)

    if (previous_name is None) or (name.lower() != previous_name.lower()):
        name_available, name_msgs = validate_project_name_available(name)
        name_ok &= name_available
        status_messages.extend(name_msgs)

    return name_ok, status_messages


def validate_project_description(description):
    """Check if the project description is non-empty.

    Parameters
    ----------
    description : str
        The project description.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    description_ok = len(description.split()) >= 3
    if description_ok:
        status_messages = []
    else:
        status_messages = [
            'Project description must have at least three words!'
        ]
    return description_ok, status_messages


def validate_project_contacts_nonempty(contacts):
    """Check if there is at least one contact.

    Parameters
    ----------
    contacts : list of dict
        The list of contacts.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = len(contacts) >= 1
    if is_ok:
        status_messages = []
    else:
        status_messages = ['There must be at least one contact!']
    return is_ok, status_messages


def validate_project_contact_addresses(contacts):
    """Check if the project contact addresses are all MIT addresses.

    Parameters
    ----------
    contacts : list of dict
        The list of contacts. Must be non-empty.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = True
    status_messages = []

    contains_plain_mit = False
    for contact in contacts:
        if not strutils.is_mit_email(contact['email']):
            is_ok = False
            status_messages.append(
                '"%s" is not an mit.edu email address!' % contact['email']
            )

        if strutils.is_plain_mit_email(contact['email']):
            contains_plain_mit = True

    if not contains_plain_mit:
        is_ok = False
        status_messages.append(
            'At least one contact must have an email address of the form '
            '"<username>@mit.edu" (otherwise no contacts will be able to edit '
            'project info).'
        )

    return is_ok, status_messages


def validate_project_contacts(contacts):
    """Check if the project contacts field is valid.

    Parameters
    ----------
    contacts : list of dict
        The list of contacts.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = True
    status_messages = []

    is_nonempty, nonempty_msgs = validate_project_contacts_nonempty(contacts)
    is_ok &= is_nonempty
    status_messages.extend(nonempty_msgs)

    if is_nonempty:
        addresses_ok, addresses_msgs = validate_project_contact_addresses(
            contacts
        )
        is_ok &= addresses_ok
        status_messages.extend(addresses_msgs)

    return is_ok, status_messages


def validate_project_roles(roles):
    """Check if the project roles all have names and descriptions.

    Parameters
    ----------
    roles : list of dict
        The list of roles.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = True
    status_messages = []
    for role in roles:
        if (len(role['role']) == 0) or (len(role['description']) == 0):
            is_ok = False
            status_messages = ['Each role must have a name and a description!']
            break
    return is_ok, status_messages


def validate_project_info(project_info, previous_name=None):
    """Validate that the given project info is OK.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project info is OK.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    is_ok = True
    status_messages = []

    name_ok, name_msgs = validate_project_name(
        project_info['name'], previous_name=previous_name
    )
    is_ok &= name_ok
    status_messages.extend(name_msgs)

    description_ok, description_msgs = validate_project_description(
        project_info['description']
    )
    is_ok &= description_ok
    status_messages.extend(description_msgs)

    contacts_ok, contacts_msgs = validate_project_contacts(
        project_info['contacts']
    )
    is_ok &= contacts_ok
    status_messages.extend(contacts_msgs)

    roles_ok, roles_msgs = validate_project_roles(project_info['roles'])
    is_ok &= roles_ok
    status_messages.extend(roles_msgs)

    # TODO: this currently allows links, comm channels, and roles to be empty.
    # Do we want to require any of those at project creation time?

    return is_ok, status_messages


def validate_add_project(project_info):
    """Validate that the given project is OK to add.

    In particular, check that:
    * The user is signed-in and is authorized to add projects.
    * The project_info is properly-formed.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project is OK to add.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    is_ok = True
    status_messages = []

    permission_ok, permission_msgs = validate_add_permission()
    is_ok &= permission_ok
    status_messages.extend(permission_msgs)

    info_ok, info_msgs = validate_project_info(project_info)
    is_ok &= info_ok
    status_messages.extend(info_msgs)

    return is_ok, status_messages


def validate_edit_permission(project_id):
    """Validate that the user has permission to edit the project.

    Parameters
    ----------
    project_id : str or int
        The project ID.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project is OK to edit.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    user = authutils.get_kerberos()
    can_edit = authutils.can_edit(user, project_id)
    if can_edit:
        return True, []
    else:
        return False, ['User is not authorized to edit this project!']


def validate_edit_project(project_info, project_id):
    """Validate that the given project is OK to edit.

    In particular, check that:
    * The user is signed-in and is authorized to edit the project.
    * The project_info is properly-formed.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int
        The ID of the project to edit.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project is OK to edit.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    is_ok = True
    status_messages = []

    permission_ok, permission_msgs = validate_edit_permission(project_id)
    is_ok &= permission_ok
    status_messages.extend(permission_msgs)

    previous_name = db.get_project_name(project_id)
    info_ok, info_msgs = validate_project_info(
        project_info, previous_name=previous_name
    )
    is_ok &= info_ok
    status_messages.extend(info_msgs)

    return is_ok, status_messages


def validate_approval_permission():
    """Check if the user has permission to approve projects.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    user = authutils.get_kerberos()
    is_ok = authutils.can_approve(user)
    if is_ok:
        status_messages = []
    else:
        status_messages = ['User is not authorized to approve projects!']
    return is_ok, status_messages


def validate_approval_action(approval_action):
    """Check if the selected approval action is valid.

    Parameters
    ----------
    approval_action : str
        The selected approval action.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = approval_action in ['approved', 'rejected']
    if is_ok:
        status_messages = []
    else:
        status_messages = [
            '"%s" is not a valid approval action!' % approval_action
        ]
    return is_ok, status_messages


def validate_approval_comments(approval_action, approver_comments):
    """Check if the approver comments are valid.

    Parameters
    ----------
    approval_action : str
        The selected approval action.
    approver_comments : str
        The reviewer's comments.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    if approval_action == 'rejected':
        is_ok = len(approver_comments.split()) >= 3
    else:
        is_ok = True

    if is_ok:
        status_messages = []
    else:
        status_messages = [
            'Comments must have at least three words when rejecting a project!'
        ]

    return is_ok, status_messages


def validate_approve_project(
    project_info, project_id, approval_action, approver_comments
):
    """Validate that the given project is OK to approve/reject, possibly
    including changes to the project info made by the reviewer.

    In particular, check that:
    * The user is signed-in and is authorized to approve projects.
    * The project_info is properly-formed.
    * If the project is to be rejected, comments have been provided.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int
        The ID of the project to edit.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project is OK to edit.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    is_ok = True
    status_messages = []

    permission_ok, permission_msgs = validate_approval_permission()
    is_ok &= permission_ok
    status_messages.extend(permission_msgs)

    previous_name = db.get_project_name(project_id)
    info_ok, info_msgs = validate_project_info(
        project_info, previous_name=previous_name
    )
    is_ok &= info_ok
    status_messages.extend(info_msgs)

    action_ok, action_msgs = validate_approval_action(approval_action)

    comments_ok, comments_msgs = validate_approval_comments(
        approval_action, approver_comments
    )
    is_ok &= comments_ok
    status_messages.extend(comments_msgs)

    return is_ok, status_messages


def validate_project_id_is_int(project_id):
    """Check if the given project ID is interpretable as an int.

    Parameters
    ----------
    project_id : str
        The project ID to check. Assumed to be a string coming from a CGI form.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    try:
        project_id = int(project_id)
    except ValueError:
        return False, ['"%s" is not a valid project ID!' % project_id]
    else:
        return True, []


def validate_project_id_exists(project_id):
    """Check if the given project ID exists (and hence can be edited).

    Parameters
    ----------
    project_id : str
        The project ID to check. Assumed to be a string coming from a CGI form.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    project_id = int(project_id)
    project_info = db.get_project(project_id)
    if len(project_info) == 0:
        is_ok = False
        status_messages = ['There is no project with id "%d"!' % project_id]
    elif len(project_info) == 1:
        is_ok = True
        status_messages = []
    else:
        is_ok = False
        status_messages = [
            'There are %d projects with id "%d"!' % (
                len(project_info), project_id
            )
        ]

    return is_ok, status_messages


def validate_project_id(project_id):
    """Check if the given project ID is OK to edit.

    Parameters
    ----------
    project_id : str
        The project ID to check. Assumed to be a string coming from a CGI form.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = True
    status_messages = []

    is_int, is_int_status = validate_project_id_is_int(project_id)
    is_ok &= is_int
    status_messages.extend(is_int_status)

    if is_int:
        is_project, is_project_status = validate_project_id_exists(project_id)
        is_ok &= is_project
        status_messages.extend(is_project_status)

    return is_ok, status_messages 
