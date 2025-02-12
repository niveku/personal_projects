from datetime import datetime

import boto3

cognito_client = boto3.client("cognito-idp")

def get_user_pool_id_by_name(pool_name: str):
    try:
        response = cognito_client.list_user_pools(MaxResults=60)

        for pool in response["UserPools"]:
            if pool["Name"] == pool_name:
                return pool["Id"]

        while "NextToken" in response:
            response = cognito_client.list_user_pools(
                MaxResults=60, NextToken=response["NextToken"]
            )
            for pool in response["UserPools"]:
                if pool["Name"] == pool_name:
                    return pool["Id"]

        return None

    except cognito_client.exceptions.ClientError as e:
        print(f">> ERROR: Not possible to find the pool {pool_name}.")
        print(f">> ERROR: {e}")
        return None


def lambda_handler(event, _context):

    email_substring = event.get("email_substring")
    user_pool_name = event.get("pool_name", "StratboxUserPool")
    user_pool_id = get_user_pool_id_by_name(user_pool_name)

    if not email_substring:
        return {"statusCode": 400, "body": "email_substring is required"}

    try:
        response = cognito_client.list_users(
            UserPoolId=user_pool_id
        )

        all_users = response.get("Users", [])

        while "PaginationToken" in response:
            response = cognito_client.list_users(
                UserPoolId=user_pool_id,
                PaginationToken=response["PaginationToken"]
            )
            all_users.extend(response.get("Users", []))

        matching_users = []
        for user in all_users:
            email = None
            last_modified = user.get("UserLastModifiedDate")
            last_modified_str = last_modified.strftime("%Y-%m-%d %H:%M:%S") if last_modified else "N/A"

            for attr in user.get("Attributes", []):
                if attr["Name"] == "email" and email_substring in attr["Value"]:
                    email = attr["Value"]
                    break

            if email:
                matching_users.append({"email": email, "last_modified": last_modified_str})

        # Generate a table-like output
        table = "Email\t\t\t\tLast Modified Date\n"
        table += "-----------------------------------------------\n"
        for user in matching_users:
            table += f"{user['email']}\t{user['last_modified']}\n"

        print(table)

        return {"statusCode": 200, "body": table}

    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

if __name__ == "__main__":
    local_event = {}
    local_event["email_substring"] = "bsp-shell"
    local_event["pool_name"] = "StratboxUserPool"
    lambda_handler(local_event, None)
