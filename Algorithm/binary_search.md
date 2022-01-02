## 이분 탐색이란?

정렬되어있는 배열에서 탐색 범위를 절반 씩 줄여나가서 탐색하는 알고리즘

## 예시 프로세스

[ 1 3 6 9 10 14 23 46 56 ] 값이 있을 때 46을 찾는다 가정  
시작점 : ◇  
끝점 : ◆  
중간점 : ★  

첫번째.

1　3　6　9　10　14　23　46　56  
◇　　　　　★　　　　　　　 ◆   

10과 46 비교 target 이 더 크기에 start 를 mid 오른쪽으로 옮김

1　3　6　9　10　14　23　46　56  
　　　　　　　　◇　★　　　 ◆   
                
23과 46 비교 target 이 더 크기에 start 를 mid 오른쪽으로 옮김

1　3　6　9　10　14　23　46　56  
　　　　　　　　　　◇　★　◆   
                    
46과 46 비교 같은 값이기에 종료  

## 시간복잡도

순차 탐색의 경우 모든 노드를 찾아야 하기에 O(N)  
이분 탐색의 경우 절반씩 줄어들기 때문에 O(logN)  

## 코드 구현 (go)

```go
import "fmt"

func main() {
	arr := []int{1, 3, 6, 9, 10, 14, 23, 46, 56}
	findIndex := binarySearch(arr, 46)
	fmt.Println(findIndex)
}

func binarySearch(arr []int, target int) int {
	start := 0
	end := len(arr) - 1

	for start <= end {
		mid := (start + end) / 2
		fmt.Println(fmt.Sprintf("Start: %d, Mid: %d, End: %d / Mid Value : %d", start, mid, end, arr[mid]))

		if arr[mid] == target {
			return mid
		} else if arr[mid] > target {
			//중간값이 찾는 값 보다 더 큰 경우 index 를 절반으로 줄이기 위해 end index 를 mid 왼쪽으로 옮김
			end = mid - 1
		} else {
			//중간값이 찾는 값 보다 더 작은 경우 index 를 절반으로 줄이기 위해 start index 를 mid 오른쪽으로 옮김
			start = mid + 1
		}
	}
	//못찾은경우 -1
	return -1
}
```

```
Start: 0, Mid: 4, End: 8 / Mid Value : 10
Start: 5, Mid: 6, End: 8 / Mid Value : 23
Start: 7, Mid: 7, End: 8 / Mid Value : 46
7
```
