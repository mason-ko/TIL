## sort interface

- 기본적으로 사용하는 정렬 알고리즘은 quick sort
- right - left 값이 12 이상 일 때 quick sort 사용
- right - left 값이 12 미만 일 때는 gap 이 6 이상이면 left + 6 => right 까지는 ShellSort 를 돌리고, 남은 부분은 삽입 정렬

## 간단하게 사용시

- 기본적으로 정의되어있는 sort package 내 IntSlice 등을 사용
- sort package 내 slice 사용 ( slice interface 객체와, less function 만 익명함수로 넣어 간편히 사용 )  
less, swap 은 reflectlite.Swapper 을 자체적으로 사용
