include .env
export

up:
	podman-compose up -d
down:
	podman-compose down
build-image:
	podman build -t eventtrakka-backend:$(IMAGE_VERSION) --build-arg CREATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
		--build-arg REVISION=$(git rev-parse HEAD) --build-arg VERSION="$(IMAGE_VERSION)" .
push-image:
	podman tag eventtrakka-backend:$(IMAGE_VERSION) ghcr.io/osca-ado-ekiti/eventtrakka-backend:$(IMAGE_VERSION)
	echo "$(GITHUB_PAT_TOKEN)" | podman login ghcr.io -u OSCA-Ado-Ekiti --password-stdin
	podman push ghcr.io/osca-ado-Ekiti/eventtrakka-backend:$(IMAGE_VERSION)