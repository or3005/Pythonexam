import sys
from jinja2 import Template
from python_terraform import Terraform
import boto3
import json


# function to get the user setting and return dictinory
def get_user_choice():
    OS=input("please choose an ubuntu [1] or amazon linux [2] OS:")
    if OS == "1":
        ami= "ami-0dee1ac7107ae9f8c"
    elif OS == "2":
        ami= "ami-0f1a6835595fb9246"   
    else:
        print("you put worng input, termniting..")
        exit(1)
    
    instance=input("please choose an instance type [1] for t2.small [2] for t2.medium :")
    
    if instance=="1":
        instance_type="t2.small"
    elif instance=="2":
        instance_type="t2.medium"
    else:
        print("you put worng input, termniting..")
        exit(1)       
        
    AZ= input("please choose and aviabilty zone :")
    
    if AZ not in ["us-east-1a", "us-east-1b"]:
     print("Invalid availability zone. You can only choose 'us-east-1a' or 'us-east-1b'.")
     AZ = input("Enter availability zone (us-east-1a or us-east-1b): ")



    LBname=input("please enter a name for load balancer : ")             
        
    return {
        "ami": ami,
        "instance_type": instance_type,
        "availability_zone": AZ,
        "region": "us-east-1",
        "load_balancer_name": LBname
    }
 
 
 #function to write the main.tf based on the template of Jinja2
 
def terraform_setup(user_inputs )-> dict:
  
  with open("terraform_template.j2","r") as template_file :
       template = Template(template_file.read())
    
  rendered_tf = template.render(user_inputs)
    
  with open("main.tf", "w") as f:
        f.write(rendered_tf)
    
  print("Terraform configuration generated in main.tf")


# function to make aws part with boto3


def aws_part(instance_id,load_dns):
    
    ec2_client = boto3.client('ec2')
    elb_client = boto3.client('elbv2')
    
    try:
     run=ec2_client.Instance()
     if run.state['Name']!= 'running' :
         print("ec2 not running, starting now")
         
         ec2_client.start_instances(InstanceIds=[instance_id])
        
      
      
     response=ec2_client.describe_instances(InstanceIds=[instance_id]).get('Reservations')
     ip=response.get('PublicIpAddress')
     instance_state=run.state['Name']
    except Exception as e:
        print("ec2  error for fetching data") 
        
        
    try:
        run=elb_client.Instance()  
        if run.state['Name']!= 'running' :
              print("LB not running, starting now")
              elb_client.start_instances(Names=[load_dns])
       
        response=elb_client.describe_load_balancers(Names=[load_dns])
        alb = response['LoadBalancers'][0]
        alb_dns_name = alb['DNSName']
    
    except Exception as e:
      print("LB DNS error for fetching data") 
      alb_dns_name="NOT FOUND"
      
    try:
        with open('aws_validation.json', 'w') as jfile:
            json.dump({
                "instance_id": instance_id,
        "instance_state": instance_state,
        "public_ip": ip,
        "load_balancer_dns": alb_dns_name
        },
        jfile
        )
        print("valdition completed")
    except Exception as e:
        print(f"error saving aws validaion to json : {str(e)}")        
        
 # function to make all the terraform commands - have a bug here see readme for mor detelis   

def run_myterraform():
    
    terraform = Terraform(working_dir=".", terraform_bin_path="C:\\Users\\orbit\\.vscode\\PyExam\\terraform.exe")

    
    try:
        
        
       # print("Terraform init output:", terraform.init())
        code, stdout, stderr = terraform.init()
        if code != 0:
            print("problome with terraform init, please try again ")
            print(stderr)
            exit(1)    
        
       #bug in this part that dont allow me to see if the rest of the code is good
       
        code=terraform.plan()
       # print("Terraform init output:", terraform.plan()) 
        print(stderr)
        if code != 0:
            print("problome with terraform plan, please try again ")
            print(stderr)
            exit(1)  
              
        code, stdout, stderr=terraform.apply(skip_plan=True)
        if code != 0:
            print("problome with terraform apply, please try again ")
            print(stderr)
            exit(1)  
              
        tfoutput=terraform.output()
        print("terraform Output:")
        print(tfoutput)
        
        instance_id= tfoutput.get('web_server_instance_id').get('value')
        load_balancer_dns = tfoutput.get('load_balancer_dns').get('value')
        
        print(f"Instance ID: {instance_id}")
        print(f"Load Balancer DNS Name: {load_balancer_dns}")
         
        aws_part(instance_id,load_balancer_dns) 
        
        
    except Exception as e :   
        
        print("Terraform execution error:", str(e))
        exit(1)
    
    
 


user_inputs=get_user_choice() 
terraform_setup(user_inputs)
run_myterraform()