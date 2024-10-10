import { Injectable, UnauthorizedException, UnprocessableEntityException } from '@nestjs/common';
import { CreateAuthDto } from './dto/create-auth.dto';
import { InjectModel } from '@nestjs/mongoose';
import { User } from 'src/user/entities/user.schema';
import { Model } from 'mongoose';
import { JwtService } from '@nestjs/jwt';
import * as argon2 from "argon2";
import { v4 } from 'uuid';
import { LoginUserDto } from 'src/user/dto/login-user.dto';

@Injectable()
export class AuthService {
  constructor(
    @InjectModel(User.name) private userModel: Model<User>,
    private readonly jwtService: JwtService,
    
  ) {}

  //Auxiliar validate function
  async validateUser(dtouser:CreateAuthDto): Promise<any> {
    const {email,password}=dtouser;
    const user = await this.userModel.findOne({ email });
    if (!user) {
      throw new UnauthorizedException('User not found');
    }
    const isPasswordValid = await argon2.verify(user.password,password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Contraseña incorrecta');
     }
    return user;
  }
//Login function
  async login(dtouser:CreateAuthDto) {
    const user = await this.validateUser(dtouser);
    const payload = { user: user.nameUser, sub: user._id };
    return {
      access_token: this.jwtService.sign(payload),
    };
  } 
//Reset password
  async resetPassword(resetDto: CreateAuthDto) {
    const { email,password } = resetDto;
    const user = await this.userModel.findOne({email:email});
    if (!user)
      throw new UnprocessableEntityException('This action can not be done');
    
    user.password = await argon2.hash(password);
    const updated = await this.userModel.findOneAndUpdate({_id:user._id}, {password:user.password});
    if(updated){
      return {
        message: 'Password account reset be done!',
      };
    }
    else{
      return {
        message: 'Fail to update',
      };
    }
  }
}