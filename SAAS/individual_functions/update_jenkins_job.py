import jenkins
import xml.etree.ElementTree as ET

def update_jenkins_job(username, password, host, job_name, new_repo_url, new_script_path, new_branch_specifier):
    server = jenkins.Jenkins(host, username=username, password=password)

    # Get the existing job configuration
    existing_config = server.get_job_config(job_name)

    # Parse the existing configuration XML
    tree = ET.fromstring(existing_config)

    # Update the repository URL and script path
    for child in tree.iter():
        if child.tag == 'repo_url':
            child.text = new_repo_url
        elif child.tag == 'script_Path':
            child.text = new_script_path
        elif child.tag == 'branch_specifier':
            child.text = new_branch_specifier

    # Convert the modified XML back to a string
    updated_config = ET.tostring(tree, encoding='utf8', method='xml').decode()

    # Update the job with the modified configuration
    server.reconfig_job(job_name, updated_config)

    return {
        'statusCode': 200,
        'body': f'Jenkins job "{job_name}" updated successfully!'
    }
