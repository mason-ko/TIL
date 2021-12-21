## 어레이 값 중 포함된 값들만 추출
ex) arr 값중 ["+","-","*"] 에 해당되는 값만 추출
```python3
ops = [x for x in ['*','+','-'] if x in expression]        
```

## 순열 함수 

코드로 작성시 아래처럼 재귀를 돌리는데
```python3
def set_ops(ops, path, item, items):
    path.append(item)
    
    if len(path) == len(ops):
        items.append(path)
        
    for x in ops:
        if x not in path:
            set_ops(ops, path.copy(), x, items)
```

permutations 임포트하여 사용 하면
```python3
from itertools import permutations

ops = [list(y) for y in permutations(ops)]    
```

## Eval
문자열 연산 가능
```python3
a = "1"
b = "+"
c = "1"
print(a + b + c)
```
= 2

## Set
Array 객체를 Object 형태로 변경 
```python3
l = set([3,1,2,3])
print(l) # {3,1,2}  << array 값은 key로 변환되기에 중복된 값은 삭제됨
```
