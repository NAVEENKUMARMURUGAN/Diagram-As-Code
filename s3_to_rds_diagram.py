from diagrams import Diagram, Cluster, Edge, Node
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.aws.database import RDSInstance
from diagrams.aws.network import PrivateSubnet, PublicSubnet, RouteTable, InternetGateway
from diagrams.aws.compute import EC2, LambdaFunction
from diagrams.aws.integration import Eventbridge
from diagrams.aws.general import Client
from diagrams.aws.security import KMS

with Diagram("S3 to RDS", show=True, direction="LR", curvestyle="ortho", outformat="png"):
    with Cluster("On-premise application"):
        app = Client("App")
        
    with Cluster("AWS"):
        
        kms = KMS("Customer Master Key")
        event_bridge = Eventbridge("Event bridge Schedule")
        s3_lambda_layer = SimpleStorageServiceS3("S3 lambda layer")
        s3_raw_layer = SimpleStorageServiceS3("S3 raw")
        s3_decrypted = SimpleStorageServiceS3("S3 decrypted")
        
        with Cluster("AWS Step functions") as step_func:
            lambda1 = LambdaFunction("Decrypt and load assurance")
            lambda2 = LambdaFunction("load to RDS")
            lambda3 = LambdaFunction("Notification")
            
        with Cluster("VPC"):
            internet_gateway = InternetGateway("Internet Gateway")
            with Cluster("Private Subnet"):
                rds_instance = RDSInstance("Postgres")
                pv_route_table = RouteTable("Route Table")
                
            with Cluster("Public Subnet"):
                ec2 =EC2("My Ec2")
                pb_route_table = RouteTable("Route Table")
            
    event_bridge >> Edge(label="triggers") >> lambda1
    
    lambda1 >> Edge(label="triggers") >> lambda2
    
    lambda2 >> Edge(label="load to rds") >> rds_instance
    
    ec2 >> Edge(label="Push Lambda Layer") >> pb_route_table
    
    pb_route_table >> Edge(label="reach IGW") >> internet_gateway
    
    internet_gateway >> Edge(label="to s3") >> s3_lambda_layer
    
    app >> Edge(label="push") >> s3_raw_layer
    
    s3_raw_layer - Edge(label="push") - lambda1
    
    lambda1 - Edge(label="write") - s3_decrypted
    
    kms - Edge(label="read secret") - lambda1
    
    [lambda1, lambda2] - Edge(label="if fails") - lambda3
    
diagram = Diagram("s3_to_rds", outformat="PNG")
            
        
