
### 맥에서 파일 업로드 시 파일명 분리되는 경우

보통 파일 업로드 시 받는 path 에 한글경로가 포함이 되어있을 때 발생

원인

한글을 처리하는 유니코드 정규화 방식이 맥과 윈도우가 다름

맥: NFD (Normalization Form Canonical Decomposition) - 정준분해   
윈도우: NFC (Normalization Form Canonical Composition) - 정준분해한 뒤에 다시 정준 결합  

맥 같은 경우 자소 단위로 Unicode 가 붙여지고 ( Hangul Jamo: 1100 ~ 11FF )  
윈도우 같은 경우 한글 호환 자모로 정준 결합되기에 (  Hangul Compatibility Jamo : 3130 ~ 318F )  

NFC로 Normalize 한 값과, NFD로 Normalize 한 값의 Bytes 부터 큰 차이가 있음 

```go
func TestJamo(t *testing.T) {
	fmt.Println("NFC: ", []byte("스크린샷"))
	fmt.Println("NFD: ", []byte("스크린샷"))
}
```
결과
```
=== RUN   TestJamo
NFC:  [236 138 164 237 129 172 235 166 176 236 131 183]
NFD:  [225 132 137 225 133 179 225 132 143 225 133 179 225 132 133 225 133 181 225 134 171 225 132 137 225 133 163 225 134 186]
--- PASS: TestJamo (0.00s)
```

---
이를 처리하기 위한 단순처리  
```go
if path != "" {
	t := transform.Chain(norm.NFD, runes.Remove(runes.In(unicode.Mn)), norm.NFC)
	path, _, _ = transform.String(t, path)
}
```

#참고  
[유니코드 등가성]  
[맥에서 한글이 자소단위로 풀어지는 현상]


[유니코드 등가성]:https://ko.wikipedia.org/wiki/%EC%9C%A0%EB%8B%88%EC%BD%94%EB%93%9C_%EB%93%B1%EA%B0%80%EC%84%B1
[맥에서 한글이 자소단위로 풀어지는 현상]:https://blog.edit.kr/entry/%EB%A7%A5%EC%97%90%EC%84%9C-%ED%95%9C%EA%B8%80%EC%9D%B4-%EC%9E%90%EC%86%8C%EB%8B%A8%EC%9C%84%EB%A1%9C-%ED%92%80%EC%96%B4%EC%A7%80%EB%8A%94-%ED%98%84%EC%83%81
