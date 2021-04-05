## sort interface

- 기본적으로 quick sort 사용
- element의 length 가 12 이상일 때 quick sort 사용
- 미만일 시 삽입정렬

## 간단하게 사용시

- 기본적으로 정의되어있는 sort package 내 IntSlice 등을 사용
- sort package 내 slice 사용 ( slice interface 객체와, less function 만 익명함수로 넣어 간편히 사용 )  
less, swap 은 reflectlite.Swapper 을 자체적으로 사용
