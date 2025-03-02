## :checkered_flag: Getting Started (For Developers)

1. Clone the Repo
2. Run `make install` to prepare development enviorment and all the packages.
3. Install and Configure AWS CLI with profile
   1. `aws configure`
4. Configure Enviornment Variables
   1. `cp .env.example .env`
5. Run `pdm dev` to start api backend on debug and development mode.
6. Run `pdm prod` to run without debug mode

## Deployment (Skip if you don't know what you are doing)

- `cd deployment.dev && terraform apply`

## Troubleshooting Inside EC2 instances

- Build from scratch and Restarting all services

```bash
su ubuntu
git clone git@github.com:skywarditsolutions/va_ai_hackathon.git /home/ubuntu/va_ai_hackathon
cd ~/va_ai_hackathon
git checkout origin trunk/dev
git pull origin trunk/dev
docker system prune -a -f --volumes
docker system up --build
```

- Applying certs

```bash
su ubuntu
cd ~/va_ai_hackathon/deployment/data
unzip cert_package.zip
cat  file_name.pem gd_bundle*.crt > fullchain.pem ## Substitute with correct file nales here
cat  private_key.txt > key.pem ## Substitute with correct file nales here
cd  ~/va_ai_hackathon
docker compose down caddy && docker compose up caddy
```
