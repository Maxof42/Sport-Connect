# Auth testing — SportConnect

Admin: admin@sportconnect.fr / Admin31! (role admin)
Club demo: club@sportconnect.fr / Club31! (role club, owns ~30 active clubs)

Auth via httpOnly cookie `access_token` (secure, samesite=none). Frontend axios uses withCredentials.

## API test
curl -c cookies.txt -X POST $URL/api/auth/login -H "Content-Type: application/json" -d '{"email":"admin@sportconnect.fr","password":"Admin31!"}'
curl -b cookies.txt $URL/api/auth/me
