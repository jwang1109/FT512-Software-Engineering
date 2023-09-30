#include <gtest/gtest.h>
#include <iostream>
#include <string.h>
#include <unordered_map>
#include <utility>

class Money;//forward declaration
class Bank;
class Sum;

//define hash function for key type std::pair<std::string,std::string>;
template<>
struct std::hash<std::pair<std::string, std::string>> {
  size_t operator()(const std::pair<std::string, std::string>& pair) const {
    return std::hash<std::string>()(pair.first) ^ std::hash<std::string>()(pair.second);
  }
};


class Expression{
public:
  virtual ~Expression(){}
  virtual void interface()=0;
  virtual Money reduce(Bank * bank,std::string to)=0;
  virtual Expression * plus(Expression * addend)=0;
  virtual Expression * times(int multiplier)=0;
  
};


class Money:public Expression{
protected:
  int amount;
  std::string currency;
public:
  void interface()override{}
  Money(int amount,std::string currency):amount(amount),currency(currency){}
  static Money dollar(int amount);
  static Money franc(int amount);
  Expression * plus(Expression * addend)override;
  Expression * times(int multiplier)override{
    return new Money(amount*multiplier,currency);
  }
  Money reduce(Bank * bank, std::string to)override;
  std::string getCurrency()const{
    return currency;
  }
  int getAmount()const{
    return amount;
  }  
  bool operator==(const Money & rhs) const{
    return amount == rhs.amount && this->currency == rhs.currency;
  }
  
};

Money Money::dollar(int amount){
  return Money(amount,"USD");
}

Money Money::franc(int amount){
  return Money(amount,"CHF");
}



class Sum:public Expression{
public:
  Expression * augend;
  Expression * addend;
  void interface()override{}
  int rate(std::string from, std::string to){
    return(from == "CHF"&& to== "USD")?2:1;
  }
  
  Sum(Expression * augend, Expression * addend):augend(augend),addend(addend){}
  Expression * plus(Expression * addend)override{
    Expression * augend = this;
    return new Sum(augend,addend);
  }
  Money reduce(Bank * bank, std::string to)override{
    int amount = augend->reduce(bank,to).getAmount() + addend->reduce(bank,to).getAmount();
    return Money(amount,to);
  }
  Expression * times(int multiplier)override{
    return new Sum(augend->times(multiplier),addend->times(multiplier));
  }
};

Expression * Money::plus(Expression * addend){
  Expression * augend = this;
  return new Sum(this,addend);
}


class Bank{
private:
  std::unordered_map<std::pair<std::string,std::string>,int> rates;// exchange rate

public:
  Money reduce(Expression * source, std::string to){
    Sum * sum = dynamic_cast<Sum*>(source);
    if(sum){
      return sum->reduce(this,to);
    }
    else{
      Money * mny = dynamic_cast<Money*>(source);
      return mny->reduce(this,to);
    }
  }
  void addRate(std::string from,std::string to,int rate){
    rates[{from,to}] = rate;
  }
  int rate(std::string from, std::string to){
    if (from == to){
      return 1;
    }
    auto it = rates.find({from,to});
    if (it != rates.end()){
      return it->second;
    }
    else{
      return-1;
    }
  }
};

Money Money::reduce(Bank * bank, std::string to){
  int rate = bank->rate(this->currency,to);
    return Money(amount/rate, to);
}

TEST(MoneyTest,SumTimesTest){
  Expression * fiveBucks = new Money(5,"USD");
  Expression * tenFrancs = new Money(10,"CHF");
  Bank bank;
  bank.addRate("CHF","USD",2);
  Expression * sum = new Sum(fiveBucks,tenFrancs);
  Money result = bank.reduce(sum->times(2),"USD");
  EXPECT_EQ(Money::dollar(20),result);      
}

TEST(MoneyTest,SumPlusMoneyTest){
  Expression * fiveBucks = new Money(5,"USD");
  Expression * tenFrancs = new Money(10,"CHF");
  Bank bank;
  bank.addRate("CHF","USD",2);
  Expression * sum = new Sum(fiveBucks,tenFrancs);
  Money result = bank.reduce(sum->plus(fiveBucks),"USD");
  EXPECT_EQ(Money::dollar(15),result);    
}

TEST(MoneyTest,MixedAdditionTest){
  Expression * fiveBucks = new Money(5,"USD");
  Expression * tenFrancs = new Money(10,"CHF");
  Bank bank;
  bank.addRate("CHF","USD",2);
  Money result = bank.reduce(fiveBucks->plus(tenFrancs),"USD");
  EXPECT_EQ(Money::dollar(10),result);
}


TEST(MoneyTest,ReduceMoneyDifferentCurrencyTest){
  Bank bank;
  bank.addRate("CHF","USD",2);
  Expression * twoFrancs = new Money(2,"CHF");
  Money result = bank.reduce(twoFrancs,"USD");
  EXPECT_EQ(Money::dollar(1),result);
}

TEST(MoneyTest,IdentityTest){
  Bank bank;
  EXPECT_EQ(1,bank.rate("USD","USD"));
}


TEST(MoneyTest, MultiplicationTest) {
  Money fiveBucks = Money::dollar(5);
  Bank bank;
  Money result_1 = bank.reduce(fiveBucks.times(2),"USD");
  Money result_2 = bank.reduce(fiveBucks.times(3),"USD");
  EXPECT_EQ(result_1,Money::dollar(10));
  EXPECT_EQ(result_2,Money::dollar(15));
}

TEST(MoneyTest,CurrencyTest){
  EXPECT_EQ("USD",Money::dollar(1).getCurrency());
  EXPECT_EQ("CHF",Money::franc(1).getCurrency());  
}

TEST(MoneyTest, EqualityTest) {
  EXPECT_TRUE(Money::dollar(5)==Money::dollar(5));
  EXPECT_FALSE(Money::dollar(5)==Money::dollar(6));
  EXPECT_FALSE(Money::franc(5)==Money::franc(6));
}

TEST(MoneyTest,ReduceSumTest){
  Expression * threeBucks = new Money(3,"USD");
  Expression * fourBucks = new Money(4,"USD");
  Expression * sum = new Sum(threeBucks,fourBucks);
  Bank bank;
  Money result = bank.reduce(sum,"USD");
  EXPECT_EQ(Money::dollar(7),result);
}

TEST(MoneyTest,ReduceMoneyTest){
  Expression * one = new Money(1,"USD");
  Bank bank;
  Money result = bank.reduce(one,"USD");
  EXPECT_EQ(Money::dollar(1),result);  
}

TEST(MoneyTest,PlusReturnSum){
  Expression * five = new Money(5,"USD");
  Expression * result = five->plus(five);
  Sum * sum = dynamic_cast<Sum*>(result);//can't use C-style (Sum) cast. Instead, try this dynamic cast.
  EXPECT_EQ(five,sum->augend);
  EXPECT_EQ(five,sum->addend);
}
