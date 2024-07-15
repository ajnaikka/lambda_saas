import jenkins
import xml.etree.ElementTree as ET

Domain_Name = "domain"
repo_url = "https://github.com/ajnaikka/ecs-infra.git"
branch_specifier= "master"
script_path = "Jenkinsfile"
xml_string = """
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.43">
  <actions/>
  <description>My Jenkins Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.91">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@4.2.2">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>{repo_url}</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>{branch_specifier}</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="list"/>
      <extensions/>
    </scm>
    <scriptPath>{script_path}</scriptPath>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
""".format(repo_url=repo_url, branch_specifier=branch_specifier, script_path=script_path)


def lambda_handler(event, context):


    username = "admin"
    password = "11484c137b9c977ecd73e01970c027a790"
    host = "http://jenkins.loyalerp.in/"
    job_name = Domain_Name

    server = jenkins.Jenkins(host, username=username, password=password) #automation_user_password

   # server.create_job(job_name,config)
    xml_string_stripped = xml_string.strip()
    tree = ET.fromstring(xml_string_stripped)
    config = ET.tostring(tree, encoding='utf8', method='xml').decode()

    server.create_job(job_name, config)
    #server.delete_job('empty')  # delete the jenkins  job