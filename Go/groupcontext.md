
## 여러 고루틴에서 Context 가 끝날때 까지 기다리는 방법

### 단일 Context 를 통한 형태로 Context 가 캔슬될때까지 기다릴 시

```go
func main(){
	
	ctx, cf := context.WithCancel(context.Background())

	for i :=0; i< 10; i ++ {
		go func(ctx context.Context) {
			fmt.Println("Server ")

			<- ctx.Done()

			fmt.Println("Server End")
		}(ctx)
	}

	cf()

	<- ctx.Done()

	fmt.Println("Real End!")
}
```

CancelFunc 실행으로 각각의 고루틴은 종료가 되겠지만 모든 고루틴이 종료될때까지 대기 될수 없음 ( 본문의 ctx.Done 이 바로 통과 )

### errgroup context 를 활용하여 모든 context 의 종료를 대기할 수 있음

```go
import “golang.org/x/sync”

func main33(){

	ctx, cf := context.WithCancel(context.Background())
	group, gctx := errgroup.WithContext(ctx)

	for i :=0; i< 10; i ++ {
		group.Go(func() error {
			fmt.Println("Server ")

			<- gctx.Done()

			fmt.Println("Server End")

			return nil
		})
	}

	cf()

	group.Wait()

	fmt.Println("Real End!")
}
```
