
## make proto 하여 생성되는 open api 의 field 명을 카멜 -> 스네이크 변경

json tag name 의 값 ( camel ) 이 아닌 proto 에서 지정한 이름 ( snake ) 형식을 쓰려면. 
Makefile proto options 에 아래 옵션

```
--openapiv2_opt json_names_for_fields=false 
```

추가!
