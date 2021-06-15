## 단일 프로세스에서 여러개의 서버 형태에서 graceful stop 구현시

server A

server B

server C

동시에 띄운 상태에서

A,B,C 중 하나라도 문제가 발생 하여
gracefulstop 을 구현 시

main 에 

parent, pCancel := context.WithCancel(context.Background())
doneChan := make(chan struct{})

를 두고

각 Server 를 errgroup 으로 고루틴을 태우고 Main 끝에서 대기를 할 수 있도록 함

문제 발생한 영역에서 close(doneChan) 호출 하거나 인터럽트를 통한 종료 시 

메인에서 doneChan 을 받아 pCancel() 을 호출하여 정상적으로 모두 종료될때까지 대기함.


```go
package main

import (
  "golang.org/x/sync/errgroup"
  "fmt"
  "os"
	"os/signal"
)

func main() {
	parent, pCancel := context.WithCancel(context.Background())
	eg, _ := errgroup.WithContext(parent)
	doneChan := make(chan struct{})

	eg.Go(func() error {
		fmt.Println("Server 1")
		<-parent.Done()
		fmt.Println("Server 1 End")
		return nil
	})

	eg.Go(func() error {
		fmt.Println("Server 2")
		<-parent.Done()
		fmt.Println("Server 2 End")
		return nil
	})

	eg.Go(func() error {
  	fmt.Println("Server 3")
		time.Sleep(time.Second*3)

		close(doneChan)
		fmt.Println("Server 3 End")
		return nil
	})

	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt, syscall.SIGTERM)
	defer close(interrupt)

	select {
	case <-doneChan:
		pCancel()
	case <-interrupt:
		pCancel()
	}

	eg.Wait()
}

```
