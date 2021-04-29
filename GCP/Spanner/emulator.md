# 설치

1. [Cloud SDK 설치.](https://cloud.google.com/sdk/install)
2. [Docker 설치.](https://docs.docker.com/docker-for-mac/install/)
3. 에뮬레이터 Run
```
gcloud emulators spanner start
```
4. 환경설정 변경
```
gcloud config configurations create emulator
gcloud config set auth/disable_credentials true
gcloud config set project my-test
gcloud config set api_endpoint_overrides/spanner http://localhost:9020/

export SPANNER_EMULATOR_HOST=localhost:9010
```

5. instance 생성

```
gcloud spanner instances create test-instance --config=emulator-config --description="Test Instance" --nodes=1
```

# 테스트 시 프로젝트가 변경되지 않았을 경우
환경변수 적용 확인 및 

vi ~/.zshrc. 
```
export SPANNER_EMULATOR_HOST=localhost:9010
```
추가



## Test Code

```go
package main

import (
	database "cloud.google.com/go/spanner/admin/database/apiv1"
	"context"
	"fmt"
	"google.golang.org/api/iterator"
	databasepb "google.golang.org/genproto/googleapis/spanner/admin/database/v1"
	"log"
)

func main(){
	ctx := context.Background()
	c, err := database.NewDatabaseAdminClient(ctx)
	if err != nil {
		// TODO: Handle error.
		log.Fatal(err)
	}

	req := &databasepb.ListDatabasesRequest{
		// TODO: Fill request struct fields.
		Parent: "projects/my-test/instances/test-instance",
	}
	it := c.ListDatabases(ctx, req)
	for {
		resp, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			// TODO: Handle error.
			log.Fatal(err)
		}
		// TODO: Use resp.
		_ = resp
		fmt.Println(resp)
	}
}
```

or

```
gcloud spanner databases list --instance=test-instance
```

+

에뮬레이터 테스트 이후, SPANNER_EMULATOR_HOST 환경 변수를 삭제해야 정상 동작됨!
