
```go
import (
    "sort"
)


func solution(tickets [][]string) []string {    
	var result []string
	for _, idx := range getSortedIndexes(tickets, "ICN") {
		check := make([]int, len(tickets))
		ret := dfs(tickets, idx, 0, check)
		if ret {
			result = append(result, tickets[idx][0]) // from
			for ;; {
				result = append(result, tickets[idx][1]) // to

				if check[idx] == 0 {
					break
				}
				idx = check[idx] - 1
			}
            break
		}
	}
	return result
}

func getSortedIndexes(tickets [][]string, target string) []int {
	type s struct {
		t string
		i int
	}
	var indexes []s

	for i, v := range tickets {
		if v[0] == target {
			indexes = append(indexes, s{
				t: v[1],
				i: i,
			})
		}
	}
	sort.Slice(indexes, func(i, j int) bool {
		it,jt := indexes[i].t, indexes[j].t
		return it < jt
	})
	ret := make([]int, len(indexes))

	for i, v := range indexes {
		ret[i] = v.i
	}

	return ret
}

func dfs(tickets [][]string, i, depth int, check []int) bool {
	if check[i] != 0 {
		return false
	}

	ticket := tickets[i]
	to := ticket[1]

	for _, idx := range getSortedIndexes(tickets, to) {
		check[i] = idx+1
		ret := dfs(tickets, idx, depth +1, check)
		if !ret {
			check[i] = 0
		} else {
			return ret
		}
	}

	return len(tickets) == depth + 1
}
```


https://programmers.co.kr/learn/courses/30/lessons/43164

출처: 프로그래머스 코딩 테스트 연습, https://programmers.co.kr/learn/challenges
